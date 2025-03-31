from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from models import Quiz, Score, Subject, Chapter, Question, db, User
from datetime import datetime, timezone
import json
from tasks import export_user_quiz_data_csv

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard", methods=["GET"])
@auth_required()
def get_dashboard():
    upcoming_quizzes = (
        Quiz.query.filter(Quiz.date_of_quiz > datetime.now(timezone.utc)).limit(5).all()
    )

    recent_scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(Score.time_stamp_of_attempt.desc())
        .limit(5)
        .all()
    )

    all_scores = Score.query.filter_by(user_id=current_user.id).all()
    total_quizzes = len(all_scores)
    avg_score = 0
    if total_quizzes > 0:
        avg_score = (
            sum(score.total_scored / score.total_possible * 100 for score in all_scores)
            / total_quizzes
        )

    return jsonify(
        {
            "upcoming_quizzes": [
                {
                    "id": quiz.id,
                    "chapter_name": quiz.chapter.name,
                    "subject_name": quiz.chapter.subject.name,
                    "date": quiz.date_of_quiz.isoformat(),
                    "duration": quiz.time_duration,
                }
                for quiz in upcoming_quizzes
            ],
            "recent_scores": [
                {
                    "quiz_id": score.quiz_id,
                    "chapter_name": score.quiz.chapter.name,
                    "score_percentage": (
                        score.total_scored / score.total_possible * 100
                    ),
                    "attempted_at": score.time_stamp_of_attempt.isoformat(),
                }
                for score in recent_scores
            ],
            "performance_stats": {
                "total_quizzes_attempted": total_quizzes,
                "average_score": round(avg_score, 2),
            },
        }
    )


@user_bp.route("/quizzes/upcoming", methods=["GET"])
@auth_required()
def get_upcoming_quizzes():
    upcoming = Quiz.query.all()

    return jsonify(
        [
            {
                "id": quiz.id,
                "chapter_id": quiz.chapter_id,
                "chapter_name": quiz.chapter.name,
                "subject_name": quiz.chapter.subject.name,
                "date_of_quiz": quiz.date_of_quiz.isoformat(),
                "time_duration": quiz.time_duration,
                "total_questions": len(quiz.questions),
            }
            for quiz in upcoming
        ]
    )


@user_bp.route("/subjects", methods=["GET"])
@auth_required()
def get_subjects():
    subjects = Subject.query.all()
    result = []
    for subject in subjects:
        subject_data = {
            "id": subject.id,
            "name": subject.name,
            "chapters": [
                {"id": chapter.id, "name": chapter.name} for chapter in subject.chapters
            ],
        }
        result.append(subject_data)
    return jsonify(result)


@user_bp.route("/quizzes/<int:id>", methods=["GET"])
@auth_required()
def get_quiz_details(id):
    quiz = Quiz.query.get_or_404(id)
    latest_attempt = quiz.get_latest_attempt(current_user.id)

    return jsonify(
        {
            "id": quiz.id,
            "status": quiz.get_status_for_user(current_user.id),
            "has_attempt": latest_attempt is not None,
            "max_attempts": quiz.max_attempts,
            "attempts_used": len(quiz.get_user_attempts(current_user.id)),
            "current_attempt": latest_attempt.attempt_number
            if latest_attempt
            else None,
        }
    )


@user_bp.route("/quizzes/<int:id>/start", methods=["POST"])
@auth_required()
def start_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    questions = Question.query.filter_by(quiz_id=id).all()

    return jsonify(
        {
            "quiz_id": quiz.id,
            "time_duration": quiz.time_duration,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question_statement,
                    "options": [q.option1, q.option2, q.option3, q.option4],
                }
                for q in questions
            ],
        }
    )


@user_bp.route("/quizzes/<int:id>/submit", methods=["POST"])
@auth_required()
def submit_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    answers = request.json.get("answers", {})

    total_possible = len(quiz.questions)
    total_scored = 0

    for question in quiz.questions:
        if str(question.id) in answers:
            if answers[str(question.id)] == question.correct_option:
                total_scored += 1

    score = Score(
        user_id=current_user.id,
        quiz_id=id,
        total_scored=total_scored,
        total_possible=total_possible,
        time_stamp_of_attempt=datetime.fromisoformat(
            request.json.get("time_stamp_of_attempt")
        ),
    )
    db.session.add(score)
    db.session.commit()

    percentage = 0
    if total_possible > 0:
        percentage = (total_scored / total_possible) * 100

    return jsonify(
        {
            "score_id": score.id,
            "total_scored": total_scored,
            "total_possible": total_possible,
            "percentage": round(percentage, 2),
        }
    )


@user_bp.route("/scores", methods=["GET"])
@auth_required()
def get_user_scores():
    scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(Score.time_stamp_of_attempt.desc())
        .all()
    )

    scores_data = []
    for score in scores:
        attempted_at_utc = score.time_stamp_of_attempt.replace(tzinfo=timezone.utc)

        percentage = 0
        total_possible = score.total_possible
        if total_possible > 0:
            percentage = round((score.total_scored / total_possible) * 100, 2)
        else:
            total_possible = len(score.quiz.questions)
            if total_possible > 0:
                percentage = round((score.total_scored / total_possible) * 100, 2)

        scores_data.append(
            {
                "quiz_id": score.quiz_id,
                "total_scored": score.total_scored,
                "total_possible": total_possible,
                "total_questions": total_possible,
                "percentage": percentage,
                "attempted_at": attempted_at_utc.isoformat(),
            }
        )
    return jsonify(scores_data)


@user_bp.route("/export/scores", methods=["POST"])
@auth_required()
def trigger_score_export():
    """
    Triggers an asynchronous job to generate and email a CSV of the user's scores.
    """
    try:
        user_id = current_user.id

        export_user_quiz_data_csv.delay(user_id)

        print(f"Queued score export task for user ID: {user_id}")

        return jsonify(
            {
                "message": "Your score export has been started. "
                "The CSV file will be emailed to you shortly."
            }
        ), 202

    except Exception as e:
        print(f"Error triggering score export for user {current_user.id}: {e}")
        return jsonify({"error": "Failed to start score export"}), 500
