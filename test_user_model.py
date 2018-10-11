"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser",
                 password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)

    def test_is_followed_by(self):
        """Does is_followed_by work?"""

        u = User(email="test@test.com", username="testuser",
                 password="HASHED_PASSWORD")

        u2 = User(
            email="second@test.com", username="testuser2", password="HASHED_PASSWORD"
        )

        u3 = User(
            email="third@test.com", username="testuser3", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # u3 follows u
        u3.following.append(u)

        self.assertEqual(u.is_followed_by(u3), True)
        self.assertEqual(u.is_followed_by(u2), False)

    def test_is_following(self):
        """Does is_following work?"""

        u = User(email="test@test.com", username="testuser",
                 password="HASHED_PASSWORD")

        u2 = User(
            email="second@test.com", username="testuser2", password="HASHED_PASSWORD"
        )

        u3 = User(
            email="third@test.com", username="testuser3", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # u3 follows u
        u3.following.append(u)

        self.assertEqual(u3.is_following(u), True)
        self.assertEqual(u.is_following(u2), False)

    def test_signup(self):
        """Does signup add user to database with expected data?"""

        u = User.signup(
            username="SlytherinSilas",
            password="HASHED_PASSWORD",
            email="test@test.com",
            image_url="http://google.com",
        )

        db.session.add(u)
        db.session.commit()

        uDB = User.query.first()

        self.assertEqual(uDB.username, "SlytherinSilas")
        self.assertEqual(uDB.messages.count(), 0)

    def test_authenticate(self):
        """Does authenticate return user when logged in with correct username and password?
        Does auth return false for incorrect password?"""

        u = User.signup(
            username="SlytherinSilas",
            password="HASHED_PASSWORD",
            email="test@test.com",
            image_url="http://google.com",
        )

        db.session.add(u)
        db.session.commit()

        user = User.authenticate("SlytherinSilas", "HASHED_PASSWORD")
        baduser = User.authenticate("SlytherinSilas", "WRONG_PASSWORD")

        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(baduser, False)
