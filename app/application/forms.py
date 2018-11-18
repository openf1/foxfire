from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms.fields import HiddenField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import ValidationError

from app.models import Application


class CreateApplicationForm(FlaskForm):
    name = StringField("Name", validators=[
        DataRequired(message="Please enter an application name")])
    description = TextAreaField("Description", validators=[
        Optional(), Length(
            max=600,
            message="Description cannot be longer than 600 characters")])

    def validate_name(self, name):
        apps = Application.query.filter_by(owner=current_user).all()
        if any(app.appname == name.data for app in apps):
            raise ValidationError("Please use a different application name")


class EditApplicationForm(CreateApplicationForm):
    aid = HiddenField()
    submit = SubmitField("Update application")

    def validate_name(self, name):
        app = Application.query.filter_by(aid=self.aid.data).first()
        # when updating name, check if already in use
        if app.appname != name.data:
            apps = Application.query.filter_by(owner=current_user).all()
            if any(app.appname == name.data for app in apps):
                raise ValidationError(
                    "Please use a different application name")
