from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Regexp
from wtforms.validators import ValidationError

from app.models import User
from app.account.forms import EditProfileForm


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Please enter your email address")])
    password = PasswordField("Password", validators=[
        DataRequired(message="Please enter your password")])
    submit = SubmitField("Sign In")


class RegistrationForm(EditProfileForm):
    password = PasswordField("Password", validators=[
        Regexp("(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",  # noqa: E501
               message="Please enter a strong password with a mix of numbers,"
                       "uppercase and lowercase letters,"
                       "and special characters")])
    password2 = PasswordField("Confirm password", validators=[
        EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Create my openf1 account")

    def validate_username(self, name):
        user = User.query.filter_by(username=name.data).first()
        if user is not None:
            raise ValidationError("Please use a different name")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Please enter an email address"),
        Email(message="Please enter a valid email address")])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[
        Regexp("(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",  # noqa: E501
               message="Please enter a strong password with a mix of numbers,"
                       "uppercase and lowercase letters,"
                       "and special characters")])
    password2 = PasswordField("Confirm Password", validators=[
        EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Request Password Reset")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Current password", validators=[
        DataRequired(message="Please enter your current password")])
    password = PasswordField("New password", validators=[
        Regexp("(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",  # noqa: E501
               message="Please enter a new password with a mix of numbers,"
                       "uppercase and lowercase letters,"
                       "and special characters")])
    password2 = PasswordField("Confirm password", validators=[
        EqualTo("password", message="Please confirm your new password")])
    submit = SubmitField("Change password")
