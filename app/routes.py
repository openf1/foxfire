from flask import redirect
from flask import render_template
from flask import url_for

from app import app
from app.forms import SigninForm


@app.route("/")
def index():
    return redirect("https://openf1.github.io", code=302)


@app.route("/account/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        return redirect(url_for("dashboard"))
    return render_template("signin.html", title="Sign In", form=form)


@app.route("/account/signup")
def signup():
    return "Sign up here!"


@app.route("/account/forgotpassword")
def forgot_password():
    return "Forgot your password!"


@app.route("/dashboard")
def dashboard():
    return "Dashboard!"
