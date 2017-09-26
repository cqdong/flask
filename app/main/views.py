from . import main
from app import db
from flask import render_template, redirect, url_for, request, flash
from datetime import datetime
from ..models import Post
from sqlalchemy import extract, func, desc
from .forms import PostForm

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    post = pagination.items
    # post = Post.query.order_by(Post.timestamp.desc())
    return render_template('index.html', posts=post, utctime=datetime.utcnow(), pagination=pagination)

@main.route('/post_new', methods=['GET', 'POST'])
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,)
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('post_new.html', forms=form)

@main.route('/post_detail/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    post.views()
    return render_template('post_detail.html', posts=post)

@main.route('/post_edit/<int:id>', methods=['GET', 'POST'])
def post_edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        return redirect(url_for('.post_detail', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('post_new.html', forms=form)