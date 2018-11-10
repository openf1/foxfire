from datetime import datetime
from flask import jsonify
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from app import db
from app.notifications import bp


@bp.route("/notifications")
@login_required
def all():
    notifications = current_user.get_notifications()
    return jsonify([{
        "name": n.name,
        "msg": n.get_data("msg"),
        "naturaltime": n.get_naturaltime(),
        "applicationId": n.get_data("applicationId"),
        "fingerprint": n.get_data("fingerprint"),
        "statusMessage": n.get_data("statusMessage"),
        "link": url_for("application.view", aid=n.get_data("applicationAid"))
    } for n in notifications])


@bp.route("/notifications/reset")
@login_required
def reset():
    current_user.reset_notifications()
    db.session.commit()
    return jsonify()
