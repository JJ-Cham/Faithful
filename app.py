#app.py 
import os 
from flask import Flask 
from models import db 


#for day 1, just making sure flask connects 
def create_app():
    app = Flask(__name__)

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
        return "Flask and the database are connected!"

    return app


app = create_app()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)