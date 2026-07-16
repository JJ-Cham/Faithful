#models.py
import os 
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    points = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    streak = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    quiz_attempts = db.relationship(
        "QuizAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(150),
        nullable=False,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    category = db.Column(
        db.String(100),
        nullable=False,
    )

    source = db.Column(
        db.String(255),
        nullable=False,
    )

    def __repr__(self):
        return f"<Reminder {self.title}>"


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(
        db.Text,
        nullable=False,
    )

    option_a = db.Column(
        db.String(255),
        nullable=False,
    )

    option_b = db.Column(
        db.String(255),
        nullable=False,
    )

    option_c = db.Column(
        db.String(255),
        nullable=False,
    )

    option_d = db.Column(
        db.String(255),
        nullable=False,
    )

    correct_answer = db.Column(
        db.String(1),
        nullable=False,
    )

    explanation = db.Column(
        db.Text,
        nullable=True,
    )

    source = db.Column(
        db.String(255),
        nullable=False,
    )

    category = db.Column(
        db.String(100),
        nullable=False,
    )

    def __repr__(self):
        return f"<QuizQuestion {self.id}>"


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(
        db.Integer,
        nullable=False,
    )

    total_questions = db.Column(
        db.Integer,
        nullable=False,
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    user = db.relationship(
        "User",
        back_populates="quiz_attempts",
    )

    def __repr__(self):
        return f"<QuizAttempt user={self.user_id} score={self.score}>"