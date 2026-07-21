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

from Api import IslamicAPIService
from models import db, User, QuizAttempt

CITY_COORDINATES = {
    "new york": (40.7128, -74.0060),
    "atlanta": (33.7490, -84.3880),
    "boston": (42.3601, -71.0589),
    "northampton": (42.3251, -72.6412),
    "chicago": (41.8781, -87.6298),
    "los angeles": (34.0522, -118.2437),
}

def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates")

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

    def get_logged_in_user():
        user_id = session.get("user_id")

        if user_id is None:
            return None

        return db.session.get(User, user_id)

    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/accept-guidelines", methods=["POST"])
    def accept_guidelines():
        agreed = request.form.get("agree")

        if agreed != "yes":
            flash(
                "You must agree to the community guidelines to continue.",
                "error",
            )
            return redirect(url_for("home"))

        session["guidelines_accepted"] = True

        return redirect(url_for("register"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            if not session.get("guidelines_accepted"):
                flash(
                    "Please review and accept the community guidelines first.",
                    "error",
                )
                return redirect(url_for("home"))

            return render_template("register.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")


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
            ), 409

        user = User(
            name=name,
            email=email,
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
            ), 409

        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name


        flash("Your account was created successfully.", "success")

        return redirect(url_for("location"))

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

        if (
            not user.selected_religion
            or not user.city
            or not user.state
            or not user.country
        ):
            flash(
                "Please complete your religion and location information.",
                "warning",
            )
            return redirect(url_for("location"))

        return redirect(url_for("community"))

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("home"))
    
    @app.route("/location")
    def location():
        user = get_logged_in_user()

        if user is None:
            flash("Please create an account or log in first.", "error")
            return redirect(url_for("login"))

        return render_template(
            "location.html",
            religion=user.selected_religion,
            city=user.city,
            state=user.state,
            country=user.country,
        )

    @app.route("/save-location", methods=["POST"])
    def save_location():
        user = get_logged_in_user()

        if user is None:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        religion = request.form.get("religion", "").strip()
        other_religion = request.form.get(
            "other_religion",
            "",
        ).strip()

        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        country = request.form.get("country", "").strip()

        if not religion:
            flash("Please select a religion.", "error")
            return redirect(url_for("location"))

        if religion == "Other":
            if not other_religion:
                flash(
                    "Please enter the name of your religion.",
                    "error",
                )
                return redirect(url_for("location"))

            religion = other_religion

        if not city:
            flash("Please enter your city.", "error")
            return redirect(url_for("location"))

        if not state:
            flash("Please enter your state or region.", "error")
            return redirect(url_for("location"))

        if not country:
            flash("Please enter your country.", "error")
            return redirect(url_for("location"))

        user.selected_religion = religion
        user.city = city
        user.state = state
        user.country = country

        db.session.commit()

        session["selected_religion"] = religion
        session["city"] = city
        session["state"] = state
        session["country"] = country

        flash(
            "Your religion and location were saved.",
            "success",
        )

        return redirect(url_for("community"))
    
    @app.route("/community")
    def community():
        user = get_logged_in_user()

        if user is None:
            flash("Please log in to find communities.", "error")
            return redirect(url_for("login"))

        if not user.selected_religion or not user.city:
            flash(
                "Please provide your religion and location first.",
                "warning",
            )
            return redirect(url_for("location"))

        city_key = user.city.strip().lower()

        latitude, longitude = CITY_COORDINATES.get(
            city_key,
            CITY_COORDINATES["new york"],
        )

        places = IslamicAPIService.get_live_community_places(
            user.selected_religion,
            latitude,
            longitude,
            city=user.city,
        )

        using_mock_data = (
            not IslamicAPIService.MAPS_KEY
            or IslamicAPIService.MAPS_KEY.startswith("mock_")
        )

        return render_template(
            "community.html",
            religion=user.selected_religion,
            city=user.city,
            state=user.state,
            country=user.country,
            places=places,
            used_default_location=city_key not in CITY_COORDINATES,
            using_mock_data=using_mock_data,
        )

    @app.route("/dashboard")
    def dashboard():
        user = get_logged_in_user()

        if user is None:
            flash("Please log in to view the dashboard.", "error")
            return redirect(url_for("login"))

        city_key = (user.city or "new york").strip().lower()

        latitude, longitude = CITY_COORDINATES.get(
            city_key,
            CITY_COORDINATES["new york"],
        )

        prayer_data = IslamicAPIService.get_prayer_times_and_date(
            latitude,
            longitude,
        )

        reminder = IslamicAPIService.get_verified_daily_reminder()

        return render_template(
            "muslim_dashboard.html",
            prayer_data=prayer_data,
            reminder=reminder,
        )
    @app.route("/quiz", methods=["GET", "POST"])
    def quiz():
        questions = IslamicAPIService.get_verified_quiz_questions()

        if request.method == "POST":
            score = 0
            results = []

            for question in questions:
                selected_answer = request.form.get(
                    f"question_{question['id']}"
                )

                is_correct = (
                    selected_answer == question["correct_answer"]
                )

                if is_correct:
                    score += 1

                results.append(
                    {
                        "id": question["id"],
                        "question": question["question"],
                        "selected_answer": selected_answer,
                        "correct_answer": question["correct_answer"],
                        "is_correct": is_correct,
                        "explanation": question["explanation"],
                        "source": question["source"],
                    }
                )

            total = len(questions)

            session["latest_quiz_score"] = score
            session["latest_quiz_total"] = total

            user = get_logged_in_user()

            if user:
                user.total_points = (user.total_points or 0) + score
                db.session.commit()

            return render_template(
                "quiz.html",
                questions=questions,
                submitted=True,
                score=score,
                total=total,
                results=results,
            )

        return render_template(
            "quiz.html",
            questions=questions,
            submitted=False,
            score=None,
            total=len(questions),
            results=[],
        )

    @app.route("/future-support")
    def future_support():
        return render_template("future_support.html", user=get_logged_in_user())

    @app.route("/profile")
    def profile():
        user = get_logged_in_user()

        if user is None:
            flash("Please log in to view your profile.", "error")
            return redirect(url_for("login"))

        return render_template(
            "profile.html",
            user=user,
            latest_quiz_score=session.get("latest_quiz_score"),
            latest_quiz_total=session.get("latest_quiz_total"),
        )

    @app.route("/api/prayer-times")
    def prayer_times():
        latitude = request.args.get(
            "latitude",
            default=40.7128,
            type=float,
        )
        longitude = request.args.get(
            "longitude",
            default=-74.0060,
            type=float,
        )

        return IslamicAPIService.get_prayer_times_and_date(
            latitude,
            longitude,
        )

    @app.route("/api/daily-reminder")
    def daily_reminder():
        return IslamicAPIService.get_verified_daily_reminder()

    return app

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
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
