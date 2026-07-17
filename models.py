import os
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()

#stores user account info, selected religion, saved location, and quiz attempts 
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

    selected_religion = db.Column(
        db.String(100),
        nullable=True,
    )

    city = db.Column(
        db.String(100),
        nullable=True,
    )

    country = db.Column(
        db.String(100),
        nullable=True,
    )

    total_points = db.Column(
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