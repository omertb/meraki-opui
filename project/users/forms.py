from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('password', validators=[DataRequired(), Length(max=128)])
    recaptcha = RecaptchaField()
