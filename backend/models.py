from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)  # email format
    password = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=False)

    role = db.Column(db.String(20), default="student", nullable=False)
    active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    scores = db.relationship("Score", backref="user", lazy=True)

    def has_role(self, role):
        return self.role == role

    def is_admin(self):
        return self.role == "admin"

    def is_student(self):
        return self.role == "student"


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # description = db.Column(db.Text, nullable=True)
    # created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    chapters = db.relationship("Chapter", backref="subject", lazy=True)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    # description = db.Column(db.Text, nullable=True)
    # created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    quizzes = db.relationship("Quiz", backref="chapter", lazy=True)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    # remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    questions = db.relationship("Question", backref="quiz", lazy=True)
    scores = db.relationship("Score", backref="quiz", lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    total_scored = db.Column(db.Integer, nullable=False)
    total_possible = db.Column(db.Integer, nullable=False)
