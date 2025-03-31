from celery import Celery
from celery.schedules import crontab
from flask_mail import Message
from flask import current_app
from datetime import datetime, timedelta, timezone
from calendar import monthrange
import io
import csv
from models import db, User, Role, Quiz, Score, Chapter, Subject


def make_celery(app):
    celery = Celery(
        app.import_name,
        CELERY_RESULT_BACKEND=app.config["CELERY_RESULT_BACKEND"],
        CELERY_BROKER_URL=app.config["CELERY_BROKER_URL"],
        include=["tasks"],
    )
    celery.conf.update(app.config)

    celery.conf.beat_schedule = {
        "send-new-quiz-reminders-daily": {
            "task": "tasks.send_new_quiz_reminders",
            "schedule": crontab(minute="*/2"),
        },
        "send-monthly-activity-report": {
            "task": "tasks.generate_monthly_reports",
            "schedule": crontab(minute="*/1"),
        },
    }

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = Celery("tasks", include=["tasks"])


@celery_app.task
def add(x, y):
    return x + y


@celery_app.task(name="tasks.send_new_quiz_reminders")
def send_new_quiz_reminders():
    mail = current_app.extensions.get("mail")
    if not mail:
        print("Mail extension not found in current app context")
        return "Task failed: Mail not configured"
    try:
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        new_quizzes = Quiz.query.filter(Quiz.created_at >= time_threshold).all()

        if not new_quizzes:
            print("No new quizzes found in the last 24 hours.")
            return "No new quizzes to notify about."

        student_role = Role.query.filter_by(name="student").first()
        if not student_role:
            print("Student role not found.")
            return "Student role missing."

        active_students = User.query.filter(
            User.roles.any(id=student_role.id), User.active == True
        ).all()

        if not active_students:
            print("No active students found.")
            return "No active students to notify."

        subject = "New Quizzes Available on Quiz Master!"
        quiz_list_html = '<ul style="list-style-type: none; padding: 0;">'
        quiz_list_text = ""
        for quiz in new_quizzes:
            chapter_name = quiz.chapter.name if quiz.chapter else "N/A"
            subject_name = (
                quiz.chapter.subject.name
                if quiz.chapter and quiz.chapter.subject
                else "N/A"
            )
            line = f"{subject_name} - {chapter_name} (Quiz ID: {quiz.id})"
            quiz_list_html += f'<li style="margin-bottom: 5px; padding: 8px; background-color: #f9f9f9; border-left: 3px solid #007bff;">{line}</li>'
            quiz_list_text += f"- {line}\n"
        quiz_list_html += "</ul>"

        body_html = f"""
        <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <p style="margin-bottom: 15px;">Hello,</p>
            <p style="margin-bottom: 10px;">New quizzes have been added in the last 24 hours:</p>
            {quiz_list_html}
            <p style="margin-top: 20px;">Log in to Quiz Master to check them out!</p>
            <p style="margin-top: 25px; font-size: 0.9em; color: #555;">Regards,<br>The Quiz Master Team</p>
        </div>
        """
        body_text = f"Hello,\n\nNew quizzes have been added in the last 24 hours:\n{quiz_list_text}\nLog in to Quiz Master to check them out!\n\nRegards,\nThe Quiz Master Team"

        with mail.connect() as conn:
            for user in active_students:
                if user.email:
                    msg = Message(
                        subject=subject,
                        recipients=[user.email],
                        body=body_text,
                        html=body_html,
                    )
                    try:
                        conn.send(msg)
                        print(f"Sent new quiz notification to {user.email}")
                    except Exception as mail_err:
                        print(f"Failed to send email to {user.email}: {mail_err}")

        return f"Sent notifications for {len(new_quizzes)} new quizzes to {len(active_students)} students."

    except Exception as e:
        print(f"Error in send_new_quiz_reminders task: {e}")
        return f"Task failed: {e}"


@celery_app.task(name="tasks.generate_monthly_reports")
def generate_monthly_reports():
    mail = current_app.extensions.get("mail")
    if not mail:
        print("Mail extension not found in current app context")
        return "Task failed: Mail not configured"
    try:
        today = datetime.now(timezone.utc)
        target_date = today - timedelta(days=15)
        year = target_date.year
        month = target_date.month
        _, num_days = monthrange(year, month)

        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(year, month, num_days, 23, 59, 59, tzinfo=timezone.utc)

        print(f"Generating monthly reports for {start_date.strftime('%Y-%m')}...")

        student_role = Role.query.filter_by(name="student").first()
        if not student_role:
            print("Student role not found.")
            return "Student role missing."

        active_students = User.query.filter(
            User.roles.any(id=student_role.id), User.active == True
        ).all()

        if not active_students:
            print("No active students found for monthly reports.")
            return "No active students to report."

        with mail.connect() as conn:
            for user in active_students:
                if not user.email:
                    print(f"Skipping user {user.id} (no email).")
                    continue

                scores = (
                    Score.query.filter(
                        Score.user_id == user.id,
                        Score.time_stamp_of_attempt >= start_date,
                        Score.time_stamp_of_attempt <= end_date,
                    )
                    .order_by(Score.time_stamp_of_attempt)
                    .all()
                )

                if not scores:
                    print(
                        f"No activity found for {user.email} in {start_date.strftime('%Y-%m')}."
                    )
                    continue

                total_attempts = len(scores)
                total_score_sum = sum(s.total_scored for s in scores)
                total_possible_sum = sum(s.total_possible for s in scores)
                average_percentage = (
                    round((total_score_sum / total_possible_sum) * 100, 2)
                    if total_possible_sum > 0
                    else 0
                )

                subject = f"Your Quiz Master Activity Report for {start_date.strftime('%B %Y')}"

                quiz_details_html = '<ul style="list-style-type: none; padding: 0;">'
                quiz_details_text = ""
                for score in scores:
                    percentage = (
                        round((score.total_scored / score.total_possible) * 100, 2)
                        if score.total_possible > 0
                        else 0
                    )
                    quiz_name = (
                        f"{score.quiz.chapter.subject.name} - {score.quiz.chapter.name}"
                        if score.quiz
                        and score.quiz.chapter
                        and score.quiz.chapter.subject
                        else f"Quiz ID {score.quiz_id}"
                    )
                    attempt_time = score.time_stamp_of_attempt.strftime(
                        "%Y-%m-%d %H:%M:%S %Z"
                    )
                    line = f"{attempt_time}: {quiz_name} - Scored {score.total_scored}/{score.total_possible} ({percentage}%)"
                    quiz_details_html += f'<li style="margin-bottom: 8px; padding: 10px; background-color: #f9f9f9; border-radius: 4px;">{line}</li>'
                    quiz_details_text += f"- {line}\n"
                quiz_details_html += "</ul>"

                body_html = f"""
                <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
                    <p style="margin-bottom: 15px;">Hello {user.full_name},</p>
                    <p style="margin-bottom: 10px;">Here's your Quiz Master activity summary for {start_date.strftime("%B %Y")}:</p>
                    <ul style="list-style-type: disc; margin-left: 20px; margin-bottom: 20px;">
                        <li style="margin-bottom: 5px;">Total Quizzes Attempted: <strong>{total_attempts}</strong></li>
                        <li style="margin-bottom: 5px;">Overall Average Score: <strong>{average_percentage}%</strong></li>
                    </ul>
                    <p style="margin-bottom: 10px;"><strong style="font-size: 1.1em;">Attempt Details:</strong></p>
                    {quiz_details_html}
                    <p style="margin-top: 20px;">Keep up the great work!</p>
                    <p style="margin-top: 25px; font-size: 0.9em; color: #555;">Regards,<br>The Quiz Master Team</p>
                </div>
                """
                body_text = f"Hello {user.full_name},\n\nActivity Report for {start_date.strftime('%B %Y')}:\n"
                body_text += f"- Total Attempts: {total_attempts}\n- Average Score: {average_percentage}%\n\nDetails:\n{quiz_details_text}\n\nKeep up the great work!\n\nRegards,\nThe Quiz Master Team"

                msg = Message(
                    subject=subject,
                    recipients=[user.email],
                    body=body_text,
                    html=body_html,
                )
                try:
                    conn.send(msg)
                    print(f"Sent monthly report to {user.email}")
                except Exception as mail_err:
                    print(f"Failed to send monthly report to {user.email}: {mail_err}")

        return f"Finished generating monthly reports for {len(active_students)} potential students."

    except Exception as e:
        print(f"Error in generate_monthly_reports task: {e}")
        return f"Monthly report task failed: {e}"


@celery_app.task(name="tasks.export_user_quiz_data_csv")
def export_user_quiz_data_csv(user_id):
    mail = current_app.extensions.get("mail")
    if not mail:
        print("Mail extension not found in current app context")
        return "Task failed: Mail not configured"
    try:
        user = User.query.get(user_id)
        if not user or not user.email:
            print(
                f"Cannot export CSV for user ID {user_id}: User not found or no email."
            )
            return f"User {user_id} invalid or missing email."

        print(f"Starting CSV export for user {user.email} (ID: {user_id})...")

        scores = (
            db.session.query(
                Score.quiz_id,
                Quiz.date_of_quiz,
                Chapter.name.label("chapter_name"),
                Subject.name.label("subject_name"),
                Score.total_scored,
                Score.total_possible,
                Score.time_stamp_of_attempt,
            )
            .join(Quiz, Score.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .join(Subject, Chapter.subject_id == Subject.id)
            .filter(Score.user_id == user_id)
            .order_by(Score.time_stamp_of_attempt.desc())
            .all()
        )

        if not scores:
            print(f"No scores found for user {user.email} (ID: {user_id}) to export.")
            return f"No scores to export for user {user_id}."

        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Quiz ID",
            "Subject",
            "Chapter",
            "Quiz Date",
            "Attempt Timestamp",
            "Score",
            "Total Possible",
            "Percentage",
        ]
        writer.writerow(headers)

        for score_data in scores:
            percentage = (
                round((score_data.total_scored / score_data.total_possible) * 100, 2)
                if score_data.total_possible > 0
                else 0
            )
            writer.writerow(
                [
                    score_data.quiz_id,
                    score_data.subject_name,
                    score_data.chapter_name,
                    score_data.date_of_quiz.strftime("%Y-%m-%d")
                    if score_data.date_of_quiz
                    else "N/A",
                    score_data.time_stamp_of_attempt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    score_data.total_scored,
                    score_data.total_possible,
                    percentage,
                ]
            )

        csv_data = output.getvalue()
        output.close()

        subject = "Your Quiz Master Score Export"
        body_text = f"Hello {user.full_name},\n\nPlease find your requested quiz score data attached as a CSV file.\n\nRegards,\nQuiz Master Team"
        body_html = f"""
        <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <p style="margin-bottom: 15px;">Hello {user.full_name},</p>
            <p style="margin-bottom: 20px;">Please find your requested quiz score data attached as a CSV file.</p>
            <p style="margin-top: 25px; font-size: 0.9em; color: #555;">Regards,<br>The Quiz Master Team</p>
        </div>
        """

        filename = (
            f"quiz_scores_{user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
        )

        msg = Message(
            subject=subject, recipients=[user.email], body=body_text, html=body_html
        )
        msg.attach(
            filename=filename, content_type="text/csv", data=csv_data.encode("utf-8")
        )

        mail.send(msg)
        print(f"Sent score export CSV to {user.email}")

        return f"Successfully exported and emailed scores for user {user_id}."

    except Exception as e:
        print(f"Error in export_user_quiz_data_csv task for user {user_id}: {e}")
        return f"CSV export task failed for user {user_id}: {e}"
