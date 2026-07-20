from app import create_app
from models import db


def build_test_app():
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "quiz-test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with test_app.app_context():
        db.create_all()

    return test_app


def test_quiz_page_displays_verified_questions():
    app = build_test_app()
    client = app.test_client()

    response = client.get("/quiz")

    assert response.status_code == 200
    assert b"How many obligatory" in response.data
    assert b"Submit all answers" in response.data


def test_quiz_submission_calculates_perfect_score():
    app = build_test_app()
    client = app.test_client()

    response = client.post(
        "/quiz",
        data={
            "answer_1": "5",
            "answer_2": "Ramadan",
            "answer_3": "Qibla",
            "answer_4": "Zakat",
            "answer_5": "Hijrah",
        },
    )

    assert response.status_code == 200
    assert b"You scored 5 out of 5" in response.data

    with client.session_transaction() as current_session:
        assert current_session["last_quiz_score"] == 5
        assert current_session["last_quiz_total"] == 5
