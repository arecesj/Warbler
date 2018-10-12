"""User views tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, Message, FollowersFollowee, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


def sign_up_user():
    """adds test user to database"""

    user = User.signup(username='JuanTon', email='test@test.com',
                       password='abc123', image_url='http://google.com')
    db.session.add(user)
    db.session.commit()
    user_in_db = User.query.first()
    return user_in_db


class UserViewsTestCase(TestCase):
    """Tests views for User model and functionality"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Like.query.delete()

        self.client = app.test_client()

        db.session.commit()

    def test_get_signup(self):
        """Does signup route work for get request?"""

        result = self.client.get('/signup')

        # Page 200s
        self.assertEquals(result.status_code, 200)

        # Signup page returns correct HTML
        self.assertIn(
            b'<h2 class="join-message">Join Warbler today.</h2>', result.data)

    def test_post_signup(self):
        """Does signup route work for post request and correctly handle duplicate usernames?"""

        data = {'username': 'JuanTon', 'password': 'abc123',
                'email': 'test@test.com', 'image_url': 'http://google.com'}

        get_request = self.client.get('/signup')
        result = self.client.post('/signup', data=data, follow_redirects=True)
        user_in_db = User.query.first()

        # Page 200s
        self.assertEquals(result.status_code, 200)

        # Post to signup page adds user to database
        self.assertEquals(user_in_db.username, "JuanTon")

        # Post to signup page returns correct HTML
        self.assertIn(
            b'<ul class="user-stats nav nav-pills">', result.data)

    def test_valid_login(self):
        """Valid login should add user_id to session and redirect home"""

        user = sign_up_user()

        resp = self.client.post(
            '/login', data={'username': user.username, 'password': 'abc123'}, follow_redirects=True)

        # The user should be added to the session
        with self.client as c:
            with c.session_transaction() as sess:
                result = sess[CURR_USER_KEY]

                self.assertEqual(result, user.id)

        # Page 200s
        self.assertEquals(resp.status_code, 200)

        # Post to login returns correct HTML
        self.assertIn(
            b'<a href="/logout">Log out</a>', resp.data)

    def test_invalid_login(self):
        """Invalid login should render users/login.html with message of Invalid credentials."""

        resp = self.client.post(
            '/login', data={'username': 'SlytherinSilas', 'password': 'wrongpw'}, follow_redirects=True)

        # Page 200s
        self.assertEquals(resp.status_code, 200)

        # Invalid login returns flashed message of invalid credentials
        self.assertIn(
            b'Invalid credentials.', resp.data)

    def test_logout(self):
        """Logout should remove user_id from session and redirect to /login"""

        user = sign_up_user()

        resp = self.client.post(
            '/login', data={'username': user.username, 'password': 'abc123'}, follow_redirects=True)

        # The user should be added to the session
        with self.client as c:
            with c.session_transaction() as sess:
                result = sess[CURR_USER_KEY]

        self.client.get('/logout', follow_redirects=True)

        # Page 200s
        self.assertEquals(resp.status_code, 200)

        # Post to login returns correct HTML
        self.assertIn(
            b'You have successfully logged out', resp.data)
