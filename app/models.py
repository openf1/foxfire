import json
import redis
import rq

from datetime import datetime as dt
from flask import current_app
from flask_login import UserMixin
from humanize import naturaltime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    company = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=dt.utcnow)
    last_seen = db.Column(db.DateTime(), default=dt.utcnow)
    last_notification_read_time = db.Column(db.DateTime)
    applications = db.relationship("Application", backref="owner",
                                   lazy="dynamic")
    notifications = db.relationship("Notification", backref="user",
                                    lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expires_in=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in)
        return s.dumps({"confirm": self.id}).decode("utf-8")

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except Exception:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expires_in=7200):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in)
        return s.dumps({"reset": self.id}).decode("utf-8")

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except Exception:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def ping(self):
        self.last_seen = dt.utcnow()
        db.session.add(self)

    def add_notification(self, name, data):
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        db.session.commit()
        return n

    def get_notifications(self):
        last_read_time = self.last_notification_read_time or dt(1900, 1, 1)
        return Notification.query.filter_by(user=self).filter(
            Notification.timestamp > last_read_time).all()

    def reset_notifications(self):
        self.last_notification_read_time = dt.utcnow()

    def get_applications(self):
        return Application.query.filter_by(owner=self).all()

    def __repr__(self):
        return "<User {}>".format(self.username)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text(), default='')
    created = db.Column(db.DateTime(), default=dt.utcnow)
    aid = db.Column(db.String(36))
    pubkey = db.Column(db.String())
    key = db.Column(db.String())
    fingerprint = db.Column(db.String(40), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='application', lazy='dynamic')

    def launch_task(self, name, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "app.tasks." + name, self.id, *args, **kwargs)
        task = Task.query.filter_by(application_id=self.aid).first()
        if task:
            db.session.delete(task)
        task = Task(id=rq_job.get_id(), application=self)
        db.session.add(task)
        db.session.commit()
        return task

    @property
    def ready(self):
        task = Task.query.filter_by(application_id=self.aid).first()
        if task:
            return task.complete
        return False

    def __repr__(self):
        return "<Application {}>".format(self.aid)


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.aid"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, redis.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    payload_json = db.Column(db.Text)

    def get_naturaltime(self):
        return naturaltime(dt.utcnow() - self.timestamp)

    def get_data(self, key=None):
        if key:
            j = json.loads(str(self.payload_json))
            return j[key]
        else:
            return json.loads(str(self.payload_json))

    def get_message(self):
        return self.get_data("msg")
