from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from models import Quiz, Score, Subject, Chapter, Question, db
from datetime import datetime, timezone
import json

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard", methods=["GET"])
@auth_required()
def get_dashboard():
    # Get upcoming quizzes (quizzes scheduled in the future)
    upcoming_quizzes = (
        Quiz.query.filter(Quiz.date_of_quiz > datetime.now(timezone.utc)).limit(5).all()
    )

    # Get recent scores
    recent_scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(Score.time_stamp_of_attempt.desc())
        .limit(5)
        .all()
    )

    # Calculate overall performance stats
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
    # Get all future quizzes
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

    if quiz.date_of_quiz.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return jsonify({"error": "Quiz has expired"}), 400

        # # Get or create attempt
        # latest_attempt = quiz.get_latest_attempt(current_user.id)

        # # If there's an incomplete attempt, use it
        # if latest_attempt and not latest_attempt.is_completed:
        #     score = latest_attempt
        # else:
        #     # Check if user has attempts remaining
        #     if not quiz.has_attempts_remaining(current_user.id):
        #         return jsonify({"error": "No attempts remaining"}), 400

    # # Create new attempt
    # score = Score(
    #     user_id=current_user.id,
    #     quiz_id=id,
    #     attempt_number=quiz.get_next_attempt_number(current_user.id),
    # )
    # db.session.add(score)
    # db.session.commit()

    questions = Question.query.filter_by(quiz_id=id).all()

    return jsonify(
        {
            "quiz_id": quiz.id,
            # "attempt_number": score.attempt_number,
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
    # latest_attempt = quiz.get_latest_attempt(current_user.id)

    # if not latest_attempt or latest_attempt.is_completed:
    #     return jsonify({"error": "No active quiz attempt found"}), 400

    answers = request.json.get("answers", {})

    # Calculate score
    total_possible = len(quiz.questions)
    total_scored = 0

    for question in quiz.questions:
        if str(question.id) in answers:
            if answers[str(question.id)] == question.correct_option:
                total_scored += 1

    # Create and save the score record
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

    # Ensure division by zero doesn't occur if total_possible is 0
    percentage = 0
    if total_possible > 0:
        percentage = (total_scored / total_possible) * 100

    return jsonify(
        {
            "score_id": score.id,  # Optionally return the new score ID
            "total_scored": total_scored,
            "total_possible": total_possible,
            "percentage": round(percentage, 2),  # Round percentage for cleaner output
            # "attempt_number": latest_attempt.attempt_number
        }
    )


@user_bp.route("/scores", methods=["GET"])
@auth_required()
def get_user_scores():
    # print(current_user.id) # Keep if useful for debugging
    scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(Score.time_stamp_of_attempt.desc())
        .all()
    )  # Added ordering

    scores_data = []
    for score in scores:
        # Assume the naive datetime from DB is UTC, make it aware
        attempted_at_utc = score.time_stamp_of_attempt.replace(tzinfo=timezone.utc)

        # Ensure division by zero doesn't occur if total_possible is 0
        percentage = 0
        total_possible = score.total_possible
        if total_possible > 0:
            percentage = round((score.total_scored / total_possible) * 100, 2)
        else:
            # Handle case where a quiz might have 0 questions (unlikely but safe)
            total_possible = len(score.quiz.questions)
            if total_possible > 0:
                percentage = round((score.total_scored / total_possible) * 100, 2)

        scores_data.append(
            {
                "quiz_id": score.quiz_id,
                "total_scored": score.total_scored,  # Added scored and possible for context
                "total_possible": total_possible,
                "total_questions": total_possible,  # Use calculated total_possible
                "percentage": percentage,
                # Format the timezone-aware datetime object to ISO format (will include 'Z' or offset)
                "attempted_at": attempted_at_utc.isoformat(),
            }
        )
    return jsonify(scores_data)


# @user_bp.route("/quiz/<int:quiz_id>/summary", methods=["GET"])
# @auth_required()
# def get_quiz_score(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     latest_attempt = quiz.get_latest_attempt(current_user.id)

#     if not latest_attempt or not latest_attempt.is_completed:
#         return jsonify({"error": "No completed attempt found"}), 404

#     return jsonify(
#         {
#             "quiz_details": {
#                 "id": quiz.id,
#                 "chapter_name": quiz.chapter.name,
#                 "subject_name": quiz.chapter.subject.name,
#                 "date_of_quiz": quiz.date_of_quiz.isoformat(),
#                 "time_duration": quiz.time_duration,
#                 "max_attempts": quiz.max_attempts,
#                 "attempts_used": len(quiz.get_user_attempts(current_user.id)),
#             },
#             "attempt_details": {
#                 "attempt_number": latest_attempt.attempt_number,
#                 "total_scored": latest_attempt.total_scored,
#                 "total_possible": latest_attempt.total_possible,
#                 "percentage": latest_attempt.score_percentage,
#                 "attempted_at": latest_attempt.time_stamp_of_attempt.isoformat(),
#             },
#         }
#     )
