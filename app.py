import os
import re

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.exc import IntegrityError

from models import User, db
from Api import IslamicAPIService

islamic_api = IslamicAPIService()

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY",
            "development-secret-key-change-later",
        ),
        SQLALCHEMY_DATABASE_URI="sqlite:///islamic_reminder.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        selected_religion = request.form.get(
            "selected_religion",
            "",
        ).strip()

        error = validate_registration(
            name=name,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )

        if error:
            flash(error, "error")
            return render_template(
                "register.html",
                name=name,
                email=email,
                selected_religion=selected_religion,
            ), 400

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash(
                "An account with that email already exists.",
                "error",
            )
            return render_template(
                "register.html",
                name=name,
                email=email,
                selected_religion=selected_religion,
            ), 409

        user = User(
            name=name,
            email=email,
            selected_religion=selected_religion or None,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "An account with that email already exists.",
                "error",
            )
            return render_template(
                "register.html",
                name=name,
                email=email,
                selected_religion=selected_religion,
            ), 409

        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name

        if user.selected_religion:
            session["selected_religion"] = user.selected_religion

        flash("Your account was created successfully.", "success")

        return redirect(url_for("community"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template(
                "login.html",
                email=email,
            ), 400

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template(
                "login.html",
                email=email,
            ), 400

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template(
                "login.html",
                email=email,
            ), 401

        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name

        if user.selected_religion:
            session["selected_religion"] = user.selected_religion

        if user.city:
            session["city"] = user.city

        if user.state:
            session["state"] = user.state

        if user.country:
            session["country"] = user.country

        flash("You are now logged in.", "success")

        return redirect(url_for("community"))

    @app.route("/logout", methods=["POST", "GET"])
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("home"))

    @app.route("/select-religion", methods=["POST"])
    def select_religion():
        religion = request.form.get("religion", "").strip()
        other_religion = request.form.get(
            "other_religion",
            "",
        ).strip()

        if not religion:
            flash("Please select a religion.", "error")
            return redirect(url_for("home"))

        if religion.lower() == "other":
            if not other_religion:
                flash(
                    "Please enter the name of the religion.",
                    "error",
                )
                return redirect(url_for("home"))

            religion = other_religion

        session["selected_religion"] = religion

        user = get_logged_in_user()

        if user:
            user.selected_religion = religion
            db.session.commit()

        return redirect(url_for("community"))

    @app.route("/save-location", methods=["POST"])
    def save_location():
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        country = request.form.get("country", "").strip()

        if not city:
            flash("Please enter a city.", "error")
            return redirect(url_for("community"))

        session["city"] = city
        session["state"] = state
        session["country"] = country

        user = get_logged_in_user()

        if user:
            user.city = city
            user.state = state or None
            user.country = country or None
            db.session.commit()

        flash("Your location was saved.", "success")

        return redirect(url_for("community"))

    @app.route("/community")
    def community():
        return render_template(
            "community.html",
            religion=session.get("selected_religion"),
            city=session.get("city"),
            state=session.get("state"),
            country=session.get("country"),
        )

    @app.route("/profile")
    def profile():
        user = get_logged_in_user()

        if user is None:
            flash("Please log in to view your profile.", "error")
            return redirect(url_for("login"))

        return render_template("profile.html", user=user)

    def get_logged_in_user():
        user_id = session.get("user_id")

        if user_id is None:
            return None

        return db.session.get(User, user_id)

    return app

    @app.route("/api/prayer-times")
    def prayer_times():
        latitude = request.args.get("latitude", default=40.7128, type=float)
        longitude = request.args.get("longitude", default=-74.0060, type=float)

        result = IslamicAPIService.get_prayer_times_and_date(
            latitude,
            longitude,
        )

        return result


    @app.route("/api/daily-reminder")
    def daily_reminder():
        reminder = IslamicAPIService.get_verified_daily_reminder()

        return reminder

def is_valid_email(email):
    """Perform basic email-format validation."""
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(email_pattern, email) is not None


def validate_registration(
    name,
    email,
    password,
    confirm_password,
):
    if not name:
        return "Name is required."

    if not email:
        return "Email is required."

    if not is_valid_email(email):
        return "Please enter a valid email address."

    if not password:
        return "Password is required."

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if password != confirm_password:
        return "Passwords do not match."

    return None


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)