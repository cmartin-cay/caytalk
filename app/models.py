from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
from app import app, db, login

blockers = db.Table('blockers',
                    db.Column('blocker_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('blocked_id', db.Integer, db.ForeignKey('user.id')),
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
    birthday = db.Column(db.DateTime)
    sex = db.Column(db.String(64))
    about_you = db.Column(db.Text)
    occupation = db.Column(db.String(64))
    comments = db.relationship('Comment', backref='commenter', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    blocked = db.relationship(
        'User', secondary=blockers,
        primaryjoin=(blockers.c.blocker_id == id),
        secondaryjoin=(blockers.c.blocked_id == id),
        backref=db.backref('blockers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

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
        return self.blocked.filter(
            blockers.c.blocked_id == user.id).count() > 0



@login.user_loader
def load_user(id):
    return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='blog_post', lazy='dynamic')

    def __repr__(self):
        return f'Post {self.body[:15]}...'

    def all_comments(self):
        blocked_comments = Comment.query.join(blockers, (blockers.c.blocked_id == Comment.user_id)).filter(blockers.c.blocker_id == current_user.id)
        _all_comments = Comment.query.filter_by(post_id=self.id)
        return _all_comments.except_(blocked_comments).order_by(Comment.timestamp.asc())

    def number_of_comments(self):
        return Comment.query.filter_by(post_id=self.id).count()


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'Comment {self.body}'
