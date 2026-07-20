#app.py 
import os 
from flask import Flask, render_template
from models import db 


#for day 1, just making sure flask connects 
def create_app():
    app = Flask(__name__, template_folder="services")

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "temporary-development-key",
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///islamic_reminder.db",
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app

    #temporaryily stores the religion in the user’s browser session.
    @app.route("/select-religion", methods=["POST"])
    def select_religion():
        religion = request.form.get("religion", "").strip()
        other_religion = request.form.get("other_religion", "").strip()

        if not religion:
            return "Please select a religion.", 400

        if religion.lower() == "other":
            if not other_religion:
                return "Please enter a religion.", 400

            religion = other_religion

        session["selected_religion"] = religion

        return redirect(url_for("location"))

    @app.route("/location", methods=["GET", "POST"])


    def location():
        if request.method == "POST":
            city = request.form.get("city", "").strip()
            country = request.form.get("country", "").strip()

            if not city or not country:
                return "City and country are required.", 400

            session["city"] = city
            session["country"] = country

            return redirect(url_for("community_finder"))

        return render_template("location.html")


    #connects place of worship to each religion, connect maps api later
    @app.route("/community")
    def community_finder():
        religion = session.get("selected_religion")
        city = session.get("city")
        country = session.get("country")

        if not religion:
            return redirect(url_for("home"))

        if not city or not country:
            return redirect(url_for("location"))

        worship_type_map = {
            "islam": "mosque",
            "christianity": "church",
            "judaism": "synagogue",
            "hinduism": "hindu temple",
            "buddhism": "buddhist temple",
            "sikhism": "gurdwara",
        }

        search_term = worship_type_map.get(
            religion.lower(),
            "place of worship",
        )

        return render_template(
            "community.html",
            religion=religion,
            city=city,
            country=country,
            search_term=search_term,
        )

    #users who select islam can continue to that page 
    @app.route("/continue")
    def continue_after_community():
        religion = session.get("selected_religion", "").lower()

        if religion == "islam":
            return redirect(url_for("muslim_dashboard"))

        return redirect(url_for("future_support"))

    @app.route("/muslim-dashboard")
    def muslim_dashboard():
        religion = session.get("selected_religion", "").lower()

        if religion != "islam":
            return redirect(url_for("future_support"))

        return render_template("muslim_dashboard.html")


    @app.route("/future-support")
    def future_support():
        religion = session.get("selected_religion", "your selected religion")

        return render_template(
            "future_support.html",
            religion=religion,
        )
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
