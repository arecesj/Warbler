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

############################
# methods for likes

    def test_like(self):
        """Does like method add a like to db and return the message object?"""

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

        result = msg_to_like.like(liker)

        committed_liker_id = Like.query.first().user_id

        committed_liked_msg_id = Like.query.first().message_id

        # does like method return the message that was liked
        self.assertEqual(result.id, msg_to_like.id)

        # does the user id for the like in the database match the user id of the user who liked the post
        self.assertEqual(committed_liker_id, liker.id)

        # does the message is for the like in the databae match the id for the message that was liked
        self.assertEqual(committed_liked_msg_id, msg_to_like.id)

    def test_unlike(self):
        """Does unlike method delete a like from db and return the message object?"""

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

        liked_msg = msg_to_like.like(liker)

        unliked_msg = liked_msg.unlike(liker)

        db_likes = Like.query.first()

        # after unliking, Like db should be empty
        self.assertEqual(unliked_msg.id, msg_to_like.id)
        self.assertEqual(db_likes, None)

    def test_is_liked_by(self):
        """Does is_liked_by method return correct boolean?"""

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
        like = Message.query.first()

        self.assertEqual(like.is_liked_by(liker), True)
        self.assertEqual(like.is_liked_by(nonliker), False)
