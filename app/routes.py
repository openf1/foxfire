from flask import redirect

from app import app


@app.route("/")
def index():
    return redirect("https://openf1.github.io", code=302)


@app.route("/accounts/signin")
def signin():
    return "Sign in here!"


@app.route("/accounts/signup")
def signup():
    return "Sign up here!"
