from . import main
from app import db
from flask import render_template, redirect, url_for, request, flash
from datetime import datetime
from ..models import Post
from sqlalchemy import extract, func, desc

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    post = pagination.items
    # post = Post.query.order_by(Post.timestamp.desc())
    return render_template('index.html', posts=post, utctime=datetime.utcnow(), pagination=pagination)