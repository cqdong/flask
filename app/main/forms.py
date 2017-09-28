from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import data_required
from app.models import Classify

class PostForm(FlaskForm):
    title = StringField('标题', validators=[data_required()])
    classify = SelectField('分类', coerce=int)
    # tag = SelectMultipleField('标签', coerce=int)
    body = TextAreaField('文章', validators=[data_required()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.classify.choices = [(c.id, c.classify) for c in Classify.query.order_by(Classify.classify).all()]
        # self.tag.choices = [(t.id, t.tag) for t in Tag.query.order_by(Tag.tag).all()]