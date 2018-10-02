from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Regexp


class SigninForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(
            message="Please enter your email address")])
    password = PasswordField(
        "Password", validators=[DataRequired(
            message="Please enter your password")])
    submit = SubmitField("Sign In")


class SignupForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired(
            message="Please enter your name")])
    email = StringField(
        "Email", validators=[
            DataRequired(message="Please enter an email address"),
            Email(message="Please enter a valid email address")])
    company = StringField(
        "Company name", validators=[DataRequired(
            message="Please enter your organization/company name")])
    password = PasswordField(
        "Password", validators=[Regexp(
            "(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",
            message="Please enter a strong password with a mix of numbers,"
                    "uppercase and lowercase letters,"
                    "and special characters")])
    confirm = PasswordField(
        "Confirm password", validators=[EqualTo("password",
            message="Passwords must match")])
    submit = SubmitField("Create my openf1 account")
