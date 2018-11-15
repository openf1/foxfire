from flask import render_template

from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(405)
def method_not_allowed(error):
    return render_template("errors/405.html"), 405


@bp.app_errorhandler(500)
def internal_error(error):  # pragma: no cover
    db.session.rollback()
    return render_template("errors/500.html"), 500
