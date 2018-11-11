from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import ChangePasswordForm
from app.auth.forms import LoginForm
from app.auth.forms import RegistrationForm
from app.auth.forms import ResetPasswordForm
from app.auth.forms import ResetPasswordRequestForm
from app.email import send_email
from app.models import User


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != "auth" \
                and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("application.dashboard"))
    return render_template("auth/unconfirmed.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("application.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash("Username or password was incorrect", "error")
            return redirect(url_for("auth.login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("application.dashboard")
        return redirect(next_page)
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("application.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    company=form.company.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account",
                   "auth/email/confirm", user=user, token=token)
        flash("A confirmation email has been sent to you")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Sign Up", form=form)


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("application.dashboard"))
    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link in invalid or expired", "error")
    return redirect(url_for("application.dashboard"))


@bp.route("/confirm")
@login_required
def resend_confirmation():
    if not current_user.confirmed:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, "Confirm Your Account",
                   "auth/email/confirm", user=current_user, token=token)
        flash("A confirmation email has been sent to you")
    return redirect(url_for("application.dashboard"))


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash("Current password could not be invalidated", "error")
            return redirect(url_for("auth.change_password"))
        current_user.password = form.password.data
        db.session.commit()
        flash("Your password has been successfully changed.")
        return redirect(url_for("application.dashboard"))
    return render_template(
        "auth/change_password.html", title="Change Password",
        user=current_user, form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("application.dashboard"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email, "Reset Your Password",
                "auth/email/reset_password", user=user, token=token)
            flash(
                "Check your email for the instructions to reset your password")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password_request.html",
                           title="Reset Password", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token=None):
    if current_user.is_authenticated:
        return redirect(url_for("application.dashboard"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password has been reset")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
