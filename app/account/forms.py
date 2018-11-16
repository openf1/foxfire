from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import ValidationError

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Name", validators=[
        DataRequired(message="Please enter your name")])
    email = StringField("Email", validators=[
        DataRequired(message="Please enter an email address"),
        Email(message="Please enter a valid email address")])
    company = StringField("Company name", validators=[
        DataRequired(message="Please enter your organization/company name")])
    submit = SubmitField("Update profile")

    def validate_username(self, name):
        if current_user.username != name.data:
            user = User.query.filter_by(username=name.data).first()
            if user is not None:
                raise ValidationError("Please use a different name")

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError("Please use a different email address")
