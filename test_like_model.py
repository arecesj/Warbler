"""Like model tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_like_model.py


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


class LikeModelTestCase(TestCase):
    """Test for Like model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()

    def test_like_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser",
                 password="HASHED_PASSWORD")

        u2 = User(
            email="second@test.com", username="testuser2", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        msg = Message(text="My dad makes margaritas!")
        u.messages.append(msg)
        db.session.commit()

        msg_to_like = Message.query.first()

        # gets the second user that was created (u2)
        liker = User.query.order_by(User.id.desc()).first()

        # gets u1
        nonliker = User.query.first()

        new_like = Like(user_id=liker.id, message_id=msg_to_like.id)
        db.session.add(new_like)
        db.session.commit()
        like = Like.query.first()

        self.assertEqual(like.user_id, liker.id)
        self.assertEqual(like.message_id, msg_to_like.id)
