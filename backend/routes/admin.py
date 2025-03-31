from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required
from models import Subject, Chapter, Quiz, Question, db, User
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/subjects", methods=["GET", "POST"])
@admin_bp.route("/subjects/<int:id>", methods=["PUT", "DELETE"])
@auth_required()
@roles_required("admin")
def manage_subjects(id=None):
    if request.method == "GET":
        subjects = Subject.query.all()
        return jsonify(
            [{"id": subject.id, "name": subject.name} for subject in subjects]
        )

    elif request.method == "POST":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        subject = Subject(name=data["name"])
        db.session.add(subject)
        try:
            db.session.commit()
            return jsonify({"id": subject.id, "name": subject.name}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Subject name must be unique"}), 400

    elif request.method == "PUT":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        subject = Subject.query.get_or_404(id)
        subject.name = data["name"]
        try:
            db.session.commit()
            return jsonify({"id": subject.id, "name": subject.name})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Subject name must be unique"}), 400

    elif request.method == "DELETE":
        subject = Subject.query.get_or_404(id)
        try:
            db.session.delete(subject)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return jsonify(
                {"error": "Cannot delete subject with existing chapters"}
            ), 400


@admin_bp.route("/subjects/<int:subject_id>/chapters", methods=["GET", "POST"])
@admin_bp.route("/chapters/<int:id>", methods=["PUT", "DELETE"])
@auth_required()
@roles_required("admin")
def manage_chapters(subject_id=None, id=None):
    if request.method == "GET":
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return jsonify(
            [
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "subject_id": chapter.subject_id,
                }
                for chapter in chapters
            ]
        )

    elif request.method == "POST":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        subject = Subject.query.get_or_404(subject_id)

        chapter = Chapter(name=data["name"], subject_id=subject_id)
        db.session.add(chapter)
        try:
            db.session.commit()
            return jsonify(
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "subject_id": chapter.subject_id,
                }
            ), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error creating chapter"}), 400

    elif request.method == "PUT":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        chapter = Chapter.query.get_or_404(id)
        chapter.name = data["name"]
        try:
            db.session.commit()
            return jsonify(
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "subject_id": chapter.subject_id,
                }
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error updating chapter"}), 400

    elif request.method == "DELETE":
        chapter = Chapter.query.get_or_404(id)
        try:
            db.session.delete(chapter)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return jsonify(
                {"error": "Cannot delete chapter with existing quizzes"}
            ), 400


@admin_bp.route("/chapters/<int:chapter_id>/quizzes", methods=["GET", "POST"])
@admin_bp.route("/quizzes/<int:id>", methods=["PUT", "DELETE"])
@auth_required()
@roles_required("admin")
def manage_quizzes(chapter_id=None, id=None):
    if request.method == "GET":
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return jsonify(
            [
                {
                    "id": quiz.id,
                    "chapter_id": quiz.chapter_id,
                    "date_of_quiz": quiz.date_of_quiz.isoformat(),
                    "time_duration": quiz.time_duration,
                    "created_at": quiz.created_at.isoformat(),
                }
                for quiz in quizzes
            ]
        )

    elif request.method == "POST":
        data = request.get_json()
        if not data or "date_of_quiz" not in data or "time_duration" not in data:
            return jsonify(
                {"error": "Date of quiz and time duration are required"}
            ), 400

        chapter = Chapter.query.get_or_404(chapter_id)

        try:
            quiz = Quiz(
                chapter_id=chapter_id,
                date_of_quiz=datetime.fromisoformat(data["date_of_quiz"]),
                time_duration=data["time_duration"],
            )
            db.session.add(quiz)
            db.session.commit()
            return jsonify(
                {
                    "id": quiz.id,
                    "chapter_id": quiz.chapter_id,
                    "date_of_quiz": quiz.date_of_quiz.isoformat(),
                    "time_duration": quiz.time_duration,
                    "created_at": quiz.created_at.isoformat(),
                }
            ), 201
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error creating quiz"}), 400

    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        quiz = Quiz.query.get_or_404(id)

        try:
            if "date_of_quiz" in data:
                quiz.date_of_quiz = datetime.fromisoformat(data["date_of_quiz"])
            if "time_duration" in data:
                quiz.time_duration = data["time_duration"]

            db.session.commit()
            return jsonify(
                {
                    "id": quiz.id,
                    "chapter_id": quiz.chapter_id,
                    "date_of_quiz": quiz.date_of_quiz.isoformat(),
                    "time_duration": quiz.time_duration,
                    "created_at": quiz.created_at.isoformat(),
                }
            )
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error updating quiz"}), 400

    elif request.method == "DELETE":
        quiz = Quiz.query.get_or_404(id)
        try:
            db.session.delete(quiz)
            db.session.commit()
            return "", 204
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(
                {"error": "Cannot delete quiz with existing questions or scores"}
            ), 400


@admin_bp.route("/quizzes/<int:quiz_id>/questions", methods=["GET", "POST"])
@admin_bp.route("/questions/<int:id>", methods=["PUT", "DELETE"])
@auth_required()
@roles_required("admin")
def manage_questions(quiz_id=None, id=None):
    if request.method == "GET":
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return jsonify(
            [
                {
                    "id": question.id,
                    "quiz_id": question.quiz_id,
                    "question_statement": question.question_statement,
                    "option1": question.option1,
                    "option2": question.option2,
                    "option3": question.option3,
                    "option4": question.option4,
                    "correct_option": question.correct_option,
                }
                for question in questions
            ]
        )

    elif request.method == "POST":
        data = request.get_json()
        required_fields = [
            "question_statement",
            "option1",
            "option2",
            "option3",
            "option4",
            "correct_option",
        ]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "All fields are required"}), 400

        if not 1 <= int(data["correct_option"]) <= 4:
            return jsonify({"error": "Correct option must be between 1 and 4"}), 400

        quiz = Quiz.query.get_or_404(quiz_id)

        question = Question(
            quiz_id=quiz_id,
            question_statement=data["question_statement"],
            option1=data["option1"],
            option2=data["option2"],
            option3=data["option3"],
            option4=data["option4"],
            correct_option=data["correct_option"],
        )
        db.session.add(question)
        try:
            db.session.commit()
            return jsonify(
                {
                    "id": question.id,
                    "quiz_id": question.quiz_id,
                    "question_statement": question.question_statement,
                    "option1": question.option1,
                    "option2": question.option2,
                    "option3": question.option3,
                    "option4": question.option4,
                    "correct_option": question.correct_option,
                }
            ), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error creating question"}), 400

    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        question = Question.query.get_or_404(id)

        if "correct_option" in data and not 1 <= data["correct_option"] <= 4:
            return jsonify({"error": "Correct option must be between 1 and 4"}), 400

        try:
            for field in [
                "question_statement",
                "option1",
                "option2",
                "option3",
                "option4",
                "correct_option",
            ]:
                if field in data:
                    setattr(question, field, data[field])

            db.session.commit()
            return jsonify(
                {
                    "id": question.id,
                    "quiz_id": question.quiz_id,
                    "question_statement": question.question_statement,
                    "option1": question.option1,
                    "option2": question.option2,
                    "option3": question.option3,
                    "option4": question.option4,
                    "correct_option": question.correct_option,
                }
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error updating question"}), 400

    elif request.method == "DELETE":
        question = Question.query.get_or_404(id)
        try:
            db.session.delete(question)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error deleting question"}), 400


@admin_bp.route("/users", methods=["GET"])
@auth_required()
@roles_required("admin")
def list_users():
    users = User.query.all()
    return jsonify(
        [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "qualification": user.qualification,
                "active": user.active,
                "roles": [role.name for role in user.roles],
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]
    )


@admin_bp.route("/users/<int:id>/toggle-active", methods=["PUT"])
@auth_required()
@roles_required("admin")
def toggle_user_active(id):
    user = User.query.get_or_404(id)

    from flask_security import current_user

    if user.id == current_user.id:
        return jsonify({"error": "Cannot modify your own access"}), 400

    user.active = not user.active
    try:
        db.session.commit()
        return jsonify({"id": user.id, "email": user.email, "active": user.active})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error updating user status"}), 400


@admin_bp.route("/users/<int:id>", methods=["DELETE"])
@auth_required()
@roles_required("admin")
def delete_user(id):
    user = User.query.get_or_404(id)

    from flask_security import current_user

    if user.id == current_user.id:
        return jsonify({"error": "Cannot delete your own account"}), 400

    try:
        db.session.delete(user)
        db.session.commit()
        return "", 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error deleting user"}), 400
