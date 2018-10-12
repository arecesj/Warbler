"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY, do_logout

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testuser2",
                                     image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_single_message(self):
        """Can you view a single message at message/<message_id>"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

            resp = c.get(f'/messages/{msg.id}')

            self.assertIn(b'<ul class="list-group no-hover" id="messages">',
                          resp.data)

    def test_logged_in_delete_message(self):
        """Can you delete a message at message/<message_id>/delete if logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

            resp = c.post(f'/messages/{msg.id}/delete')

            msg_db = Message.query.first()

            # after successful delete, page should redirect
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(msg_db, None)

    def test_logged_out_delete_message(self):
        """If logged out user tries to delete message, should redirect to homepage"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()

        with self.client as c:
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)

            msg_db = Message.query.first()

            # after successful delete, page should follow redirect
            self.assertEqual(resp.status_code, 200)

            # message in database should still exist
            self.assertIn("Hello", msg_db.text)

            # html response should contain message that access is denied
            self.assertIn(b"Access unauthorized", resp.data)


################################################
# tests for likes

    def test_like_message(self):
        """Can user like a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            c.post("/messages/new", data={"text": "Hello"})

            # gets the user who is logged in (testuser)
            liker = User.query.first()
            msg_to_like = Message.query.first()

            # testuser likes her own post
            resp = c.post(f'like/{msg_to_like.id}',
                          data={'return_to': f'/users/{liker.id}'}, follow_redirects=True)

            # Make sure it follows redirect
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertIn(b'<i class="fas fa-star pl-1">', resp.data)

    def test_unlike_message(self):
        """Can user unlike a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            # gets the user who is logged in (testuser)
            liker = User.query.first()
            msg_to_like = Message.query.first()

            # testuser likes her own post
            c.post(f'like/{msg_to_like.id}',
                   data={'return_to': f'/users/{liker.id}'}, follow_redirects=True)

            # testuser unlikes her post
            resp = c.post(f'unlike/{msg_to_like.id}',
                          data={'return_to': f'/users/{liker.id}'}, follow_redirects=True)

            # Make sure it follows redirect
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertIn(b'<i class="far fa-star pl-1">', resp.data)

    def test_404(self):
        """Does 404 page load"""

        resp = self.client.get('/fakeroute')

        self.assertEqual(resp.status_code, 404)
        self.assertIn(b'404. Page not found', resp.data)
