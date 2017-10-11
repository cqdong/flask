from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import data_required, Length, Email

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[data_required(), Length(1, 64)])
    password = PasswordField('密码', validators=[data_required()])
    remeber_me = BooleanField('记住我')
    submit = SubmitField('登陆')