from flask import flash
from flask import redirect
from flask import render_template
from flask import send_file
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_wtf import FlaskForm
from io import BytesIO
from uuid import uuid4

from app import db
from app.application import bp
from app.application.forms import CreateApplicationForm
from app.application.forms import EditApplicationForm
from app.models import Application


@bp.route("/")
@login_required
def dashboard():
    return render_template("application/dashboard.html", title="Applications",
                           user=current_user)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateApplicationForm()
    if form.validate_on_submit():
        application = Application(appname=form.name.data,
                                  description=form.description.data,
                                  aid=str(uuid4()),
                                  owner=current_user)
        db.session.add(application)
        db.session.commit()
        application.launch_task("gen_app_key", current_user.id)
        return redirect(url_for("application.dashboard"))
    return render_template("application/create.html",
                           title="Create Application", user=current_user,
                           form=form)


@bp.route("/view/<aid>")
@login_required
def view(aid):
    current_app = Application.query.filter_by(aid=aid).first()
    if not current_app:
        return render_template("application/errors/app_not_found.html")
    form = FlaskForm(obj=current_app)
    return render_template("application/view.html",
                           title="Application Details", user=current_user,
                           application=current_app, form=form)


@bp.route("/edit/<aid>", methods=["GET", "POST"])
@login_required
def edit(aid):
    current_app = Application.query.filter_by(aid=aid).first()
    if not current_app:
        return render_template("application/errors/app_not_found.html")
    form = EditApplicationForm(obj=current_app)
    if form.validate_on_submit():
        current_app.appname = form.name.data
        current_app.description = form.description.data
        db.session.commit()
        flash("Your application details have been successfully updated.")
        return redirect(url_for("application.view", aid=aid))
    return render_template("application/edit.html",
                           title="Edit Application Details",
                           application=current_app, user=current_user,
                           form=form)


@bp.route("/delete/<aid>", methods=["POST"])
@login_required
def delete(aid):
    current_app = Application.query.filter_by(aid=aid).first()
    if not current_app:
        return render_template("application/errors/app_not_found.html")
    form = FlaskForm(obj=current_app)
    if form.validate_on_submit():
        db.session.delete(current_app)
        db.session.commit()
        flash("Your application has been deleted.")
    return redirect(url_for("application.dashboard"))


@bp.route("/renew/<aid>", methods=["POST"])
@login_required
def renew(aid):
    current_app = Application.query.filter_by(aid=aid).first()
    if not current_app:
        return render_template("application/errors/app_not_found.html")
    form = FlaskForm(obj=current_app)
    if form.validate_on_submit():
        current_app.launch_task("renew_app_key", current_user.id)
        return redirect(url_for("application.dashboard"))
    return redirect(url_for("application.view", aid=aid))


@bp.route("/download/<aid>")
@login_required
def download(aid):
    current_app = Application.query.filter_by(aid=aid).first()
    if not current_app:
        return render_template("application/errors/app_not_found.html")
    filename = "{}.pem".format(current_app.fingerprint[0:8])
    bio = BytesIO('{}'.format(current_app.key).encode())
    return send_file(bio, as_attachment=True, attachment_filename=filename)
