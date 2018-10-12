"""User views tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler_test"


# Now we can import app

from app import app, signup

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """Tests views for User model and functionality"""

    def setUp(self):
        """Create test client, add sample data."""

        FollowersFollowee.query.delete()
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

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

        result = self.client.post('/signup', data=data, follow_redirects=True)

        # with self.client:
        #     result = self.client.post(
        #         '/signup', data=data, follow_redirects=True)
        #     self.assertTrue(session['curr_user'])

        user_in_db = User.query.first()

        # Page 200s
        self.assertEquals(result.status_code, 200)

        # Post to signup page adds user to database
        self.assertEquals(user_in_db.username, "JuanTon")

        # Post to signup page returns correct HTML
        # self.assertIn(
        #     b'<ul class="user-stats nav nav-pills">', result.data)
