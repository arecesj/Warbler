"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class FollowersFollowee(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = "follows"

    followee_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True
    )

    follower_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    image_url = db.Column(db.Text, default="/static/images/default-pic.png")

    header_image_url = db.Column(db.Text, default="/static/images/warbler-hero.jpg")

    bio = db.Column(db.Text)

    location = db.Column(db.Text)

    password = db.Column(db.Text, nullable=False)

    messages = db.relationship("Message", backref="user", lazy="dynamic")

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(FollowersFollowee.follower_id == id),
        secondaryjoin=(FollowersFollowee.followee_id == id),
        backref=db.backref("following", lazy="dynamic"),
        lazy="dynamic",
    )

    likes = db.relationship("Like", backref="user", lazy="dynamic")

    liked_messages = db.relationship(
        "Message",
        secondary="likes",
        backref=db.backref("liking_users", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        return bool(self.followers.filter_by(id=other_user.id).first())

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        return bool(self.following.filter_by(id=other_user.id).first())

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username, email=email, password=hashed_pwd, image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(140), nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    likes = db.relationship("Like", backref="message", lazy="dynamic")

    # "Fat models, thin views"

    def is_liked_by(self, user):
        """Does this user like this message?"""

        return bool(self.liking_users.filter_by(id=user.id).first())

    def like(self, user):
        """when a message is liked, adds like to database"""

        new_like = Like(user_id=user.id, message_id=self.id)

        db.session.add(new_like)
        db.session.commit()

        return self

    def unlike(self, user):
        """when a messae is unliked, delete like from database"""

        like = Like.query.filter(
            Like.message_id == self.id, Like.user_id == user.id
        ).first()
        db.session.delete(like)
        db.session.commit()

        return self


class Like(db.Model):
    """Connection btw Message and User who liked Message"""

    __tablename__ = "likes"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True
    )

    message_id = db.Column(
        db.Integer, db.ForeignKey("messages.id", ondelete="cascade"), primary_key=True
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
