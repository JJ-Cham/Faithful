# tests/test_database.py

import pytest

from app import create_app
from models import User, db


@pytest.fixture
def app():
    """Create a Flask app configured with a temporary test database."""

    test_app = create_app()

    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with test_app.app_context():
        db.drop_all()
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


def test_user_can_be_saved_to_database(app):
    """Verify that a user can be added and retrieved."""

    with app.app_context():
        user = User(
            name="Test User",
            email="test@example.com",
            selected_religion="Islam",
            city="New York",
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
        assert saved_user.country == "United States"
        assert saved_user.check_password("password123") is True
        assert saved_user.password_hash != "password123"