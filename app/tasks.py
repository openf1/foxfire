import sys
import time

from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from rq import get_current_job

from app import create_app
from app import db
from app.models import Application
from app.models import Task
from app.models import User

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:  # pragma: no cover
        job.meta['progress'] = progress
        job.save_meta()

        if progress >= 100:
            task = Task.query.get(job.get_id())
            task.complete = True
            db.session.commit()


def _set_notification(user_id, payload):
    user = User.query.get(user_id)
    user.add_notification("unread_message_count", payload)


def _gen_key(application):
    _set_task_progress(0)

    key = RSA.generate(2048)
    time.sleep(2)
    _set_task_progress(25)

    application.pubkey = key.publickey().export_key()
    time.sleep(2)
    _set_task_progress(50)

    application.key = key.export_key()
    time.sleep(2)
    _set_task_progress(75)

    h = SHA1.new()
    h.update(key.export_key())
    fingerprint = h.hexdigest()
    application.fingerprint = fingerprint
    time.sleep(2)
    _set_task_progress(100)

    return fingerprint


def gen_app_key(application_id, user_id):
    try:
        app = Application.query.get(application_id)
        fingerprint = _gen_key(app)
        payload = {
            "msg": "Your new application "
                   "<strong class='text-info'>{}</strong> "
                   "is ready".format(app.appname),
            "statusMessage": "Your application is ready",
            "applicationId": application_id,
            "applicationAid": app.aid,
            "fingerprint": fingerprint
        }
        _set_notification(user_id, payload)
    except Exception:  # pragma: no cover
        _set_task_progress(100)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
    finally:
        return


def renew_app_key(application_id, user_id):
    try:
        app = Application.query.get(application_id)
        fingerprint = _gen_key(app)
        payload = {
            "msg": "Application keys for "
                   "<strong class='text-info'>{}</strong> "
                   "have been renewed".format(app.appname),
            "statusMessage": "Your application is ready",
            "applicationId": application_id,
            "applicationAid": app.aid,
            "fingerprint": fingerprint
        }
        _set_notification(user_id, payload)
    except Exception:  # pragma: no cover
        _set_task_progress(100)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
    finally:
        return
