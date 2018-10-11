"""Message model tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_model.py


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


class MessageModelTestCase(TestCase):
    """Test for Message model and functionality"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser",
                 password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        msg = Message(text="My dad makes margaritas!")
        u.messages.append(msg)
        db.session.commit()

        # User should have 1 message with text of "My dad makes margaritas!"
        self.assertEqual(u.messages.count(), 1)
        self.assertIn("My dad", u.messages.first().text)
