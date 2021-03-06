from datetime import datetime
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from app import db, login

blockers = db.Table(
    "blockers",
    db.Column("blocker_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("blocked_id", db.Integer, db.ForeignKey("user.id")),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    about_you = db.Column(db.Text)
    comments = db.relationship("Comment", backref="commenter", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    blocked = db.relationship(
        "User",
        secondary=blockers,
        primaryjoin=(blockers.c.blocker_id == id),
        secondaryjoin=(blockers.c.blocked_id == id),
        backref=db.backref("blockers", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def block(self, user):
        if not self.is_blocking(user):
            self.blocked.append(user)

    def unblock(self, user):
        if self.is_blocking(user):
            self.blocked.remove(user)

    def is_blocking(self, user):
        return self.blocked.filter(blockers.c.blocked_id == user.id).count() > 0


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    url = db.Column(db.Text)
    source = db.Column(db.Text, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", backref="blog_post", lazy="dynamic")

    def __repr__(self):
        return f"Post {self.title[:15]}..."

    def show_comments(self):
        all_comments = Comment.query.filter_by(post_id=self.id)
        # This hides the comments from people that you have blocked
        blocked_comments = all_comments.join(
            blockers, (blockers.c.blocked_id == Comment.user_id)
        ).filter(blockers.c.blocker_id == current_user.id)
        # This prevents the people that you have blocked from seeing your comments
        blocked_by_comments = all_comments.join(
            blockers, (blockers.c.blocker_id == Comment.user_id)
        ).filter(blockers.c.blocked_id == current_user.id)
        return (
            all_comments.except_(blocked_comments)
            .except_(blocked_by_comments)
            .order_by(Comment.timestamp.asc())
        )

    def number_of_comments(self):
        return Comment.query.filter_by(post_id=self.id).count()

    def set_source(self, full_url):
        parsed_url = urlparse(full_url)
        self.source = parsed_url.netloc


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    def __repr__(self):
        return f"Comment {self.body}"
