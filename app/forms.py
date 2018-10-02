from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class SigninForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(
            message="Please enter your email address")])
    password = PasswordField(
        "Password", validators=[DataRequired(
            message="Please enter your password")])
    submit = SubmitField("Sign In")


class SignupForm(FlaskForm):
    pass

