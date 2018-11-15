from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user
from flask_wtf import FlaskForm

from app import db
from app.account import bp
from app.account.forms import EditProfileForm


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.company = form.company.data
        db.session.commit()
        flash("Your profile has been successfully updated.")
        return redirect(url_for("account.edit"))
    return render_template("account/edit.html", title="Profile",
                           user=current_user, form=form)


@bp.route("/delete", methods=["POST"])
@login_required
def delete():
    form = FlaskForm()
    if form.validate_on_submit():
        for application in current_user.applications.all():
            db.session.delete(application)
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash("Your account has been deleted.")
        return redirect(url_for("auth.register"))
    return redirect(url_for("account.edit"))
