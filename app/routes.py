from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

from app import app
from app.forms import SigninForm
from app.forms import SignupForm


@app.route("/")
def index():
    return redirect("https://openf1.github.io", code=302)


@app.route("/account/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        return redirect(url_for("dashboard"))
    if form.errors:
        flash("Username or password was incorrect")
    return render_template("signin.html", title="Sign In", form=form)


@app.route("/account/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        return "Welcome!"
    return render_template("signup.html", title="Sign Up", form=form)


@app.route("/account/forgotpassword")
def forgot_password():
    return "Forgot your password!"


@app.route("/dashboard")
def dashboard():
    return "Dashboard!"
