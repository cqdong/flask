from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from . import db, login_manager
from markdown import markdown
import bleach
from bs4 import BeautifulSoup as bs
from werkzeug.security import generate_password_hash, check_password_hash


registrations = db.Table('registrations',
                         db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                         db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                         )

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    body_digest = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    view = db.Column(db.Integer, default=0)
    classify_id = db.Column(db.Integer, db.ForeignKey('classifys.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiatior):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'p', 'img']
        attr = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt']
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html', extensions=['markdown.extensions.extra']),
            tags=allowed_tags, strip=True,attributes=attr
        ))

        num = 1
        tags = ''
        tags_begin = False
        abstract = ''
        for i in target.body_html:
            if num <= 300:
                if i == '<':
                    tags_begin = True
                elif i == '>':
                    tags += i
                    abstract += tags
                    tags = ''
                    tags_begin = False
                    continue
                if tags_begin:
                    tags += i
                else:
                    abstract += i
                    num += 1
        target.body_digest = bs(abstract, 'html.parser').prettify()

    def views(self):
        self.view += 1
        db.session.add(self)

    def __repr__(self):
        return '<POST %r>' %self.title

class Classify(db.Model):
    __tablename__ = 'classifys'
    id = db.Column(db.Integer, primary_key=True)
    classify = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post', backref='post_classify', lazy='dynamic')

    def __repr__(self):
        return "<CLASSIFY %r>"%self.classify

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post',
                            secondary=registrations,
                            backref=db.backref('post_tag', lazy='dynamic'))
    def __repr__(self):
        return '<TAG %r>'%self.tag

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    real_name = db.Column(db.String(64))
    location = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    @property
    def password(self):
        return AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<USER %r>'%self.username

db.event.listen(Post.body, 'set', Post.on_changed_body)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))