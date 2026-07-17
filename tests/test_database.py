import pytest

from app import create_app
from models import User, db


@pytest.fixture
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_user_can_be_saved_to_database(app):
    with app.app_context():
        user = User(
            name="Test User",
            email="test@example.com",
            selected_religion="Islam",
            city="New York",
            state="New York",
            country="United States",
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(
            email="test@example.com"
        ).first()

        assert saved_user is not None
        assert saved_user.name == "Test User"
        assert saved_user.email == "test@example.com"
        assert saved_user.selected_religion == "Islam"
        assert saved_user.city == "New York"
        assert saved_user.state == "New York"
        assert saved_user.country == "United States"

        assert saved_user.password_hash != "password123"
        assert saved_user.check_password("password123") is True
        assert saved_user.check_password("wrong-password") is False


def test_duplicate_email_is_rejected(client, app):
    first_response = client.post(
        "/register",
        data={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "selected_religion": "Islam",
        },
        follow_redirects=False,
    )

    second_response = client.post(
        "/register",
        data={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "password456",
            "confirm_password": "password456",
            "selected_religion": "Islam",
        },
        follow_redirects=False,
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 409

    with app.app_context():
        users = User.query.filter_by(
            email="duplicate@example.com"
        ).all()

        assert len(users) == 1
        assert users[0].name == "First User"