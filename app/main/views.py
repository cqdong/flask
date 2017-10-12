from . import main
from app import db
from flask import render_template, redirect, url_for, request, flash, current_app, jsonify, Response
from datetime import datetime
from ..models import Post, Classify, Tag
from sqlalchemy import extract, func, desc
from .forms import PostForm
import os
from flask_login import login_required, current_user

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    post = pagination.items
    # post = Post.query.order_by(Post.timestamp.desc())
    return render_template('index.html', posts=post, utctime=datetime.utcnow(), pagination=pagination)

@main.route('/post_new', methods=['GET', 'POST'])
@login_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        tag_list = []
        for t in form.tag.data:
            tag_list.append(Tag.query.get(t))
        post = Post(title=form.title.data, body=form.body.data,post_classify=Classify.query.get(form.classify.data),
                    post_tag=tag_list)
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('post_new.html', forms=form)

@main.route('/post_detail/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    post.views()
    return render_template('post_detail.html', posts=post)

@main.route('/post_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def post_edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.post_classify = Classify.query.get(form.classify.data)
        tags = []
        for t in form.tag.data:
            tags.append(Tag.query.get(t))
        post.post_tag = tags
        db.session.add(post)
        return redirect(url_for('.post_detail', id=post.id))
    post_tags = []
    tag_temp = post.post_tag.all()
    # if tag_temp:
    for t in tag_temp:
        post_tags.append(t.id)
    form.tag.default = post_tags
    form.classify.default = post.classify_id
    form.process()
    form.title.data = post.title
    form.body.data = post.body
    return render_template('post_new.html', forms=form)

@main.route('/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files.get('editormd-image-file')
    if not file:
        res = {
            'success': 0,
            'massage': '图片格式异常'
        }
    else:
        ex = os.path.splitext(file.filename)[1]
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + ex
        file.save(os.path.join(current_app.static_folder, 'img', filename))
        res = {
            'success': 1,
            'massage': '图片上传成功',
            'url': url_for('.image', name=filename)
        }
    return jsonify(res)

@main.route('/image/<name>')
def image(name):
    with open(os.path.join(current_app.static_folder, 'img', name), 'rb') as f:
        resp = Response(f.read(), mimetype='image/jpeg')
    return resp

@main.route('/archive')
def archive():
    post = []
    years = db.session.query(extract('year', Post.timestamp).label('year'),
                             func.count('*').label('year_count')).group_by('year').order_by(desc('year')).all()
    for y in years:
        post.append([y[0], db.session.query(Post).filter(extract('year', Post.timestamp) == y[0]).order_by(
            desc(Post.timestamp)).all()])
    return render_template('archive.html', posts=post)

@main.route('/classify')
def classify():
    post = Classify.query.all()
    return render_template('classify.html', posts=post)

@main.route('/classify/<int:id>')
def classify_list(id):
    post = Classify.query.get_or_404(id).posts.order_by(Post.timestamp.desc()).all()
    return render_template('classify_list.html', posts=post)

@main.route('/tag')
def tag():
    post = Tag.query.all()
    return render_template('tag.html', posts=post)

@main.route('/tag/<int:id>')
def tag_list(id):
    tag = Tag.query.get_or_404(id)
    post = tag.posts
    return render_template('tag_list.html', posts=post, tags=tag)