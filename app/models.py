from flask import current_app, request, url_for
from datetime import datetime
from . import db
from markdown import markdown
import bleach
from bs4 import BeautifulSoup as bs

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

db.event.listen(Post.body, 'set', Post.on_changed_body)