import json
import time

from datetime import datetime
from flask_testing import TestCase

from app import create_app
from app import db
from app.models import Application
from app.models import Notification
from app.models import Task
from app.models import User


class UserModelTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expires_in=1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'dog'))
        self.assertTrue(u.verify_password('cat'))

    def test_expired_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token(expires_in=1)
        time.sleep(2)
        self.assertFalse(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('cat'))

    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_add_notification(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        u.add_notification(name='test', data={'a': 'b'})
        n = u.get_notifications()
        self.assertTrue(len(n) == 1)
        u.add_notification(name='test', data={'c': 'd'})
        n = u.get_notifications()
        self.assertTrue(len(n) == 2)

    def test_reset_notification(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        u.add_notification(name='test', data={'a': 'b'})
        u.add_notification(name='test', data={'c': 'd'})
        u.reset_notifications()
        n = u.get_notifications()
        self.assertTrue(len(n) == 0)

    def test_add_get_reset_notification(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        u.add_notification(name='test', data={'a': 'b'})
        u.add_notification(name='test', data={'c': 'd'})
        n = u.get_notifications()
        self.assertTrue(len(n) == 2)
        u.reset_notifications()
        u.add_notification(name='test', data={'e': 'f'})
        n = u.get_notifications()
        self.assertTrue(len(n) == 1)

    def test_user_repr(self):
        u = User(username='john')
        self.assertTrue(u.__repr__() == '<User john>')


class ApplicationModelTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_application_launch_task(self):
        app = Application(aid='123456789')
        db.session.add(app)
        db.session.commit()
        task = app.launch_task('test')
        self.assertTrue(task is not None)

    def test_application_launch_task_existing_aid(self):
        app = Application(aid='123456789')
        db.session.add(app)
        db.session.commit()
        task1 = app.launch_task('test')
        task2 = app.launch_task('test2')

        t = Task.query.filter_by(application_id='123456789').first()
        self.assertTrue(t.id != task1.id)
        self.assertTrue(t.id == task2.id)

    def test_application_repr(self):
        app = Application(aid='123456789')
        self.assertTrue(app.__repr__() == '<Application 123456789>')


class TaskModelTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_rq_job(self):
        app = Application(aid='123456789')
        task = app.launch_task('test')
        self.assertTrue(task.get_rq_job() is not None)

    def test_get_progress(self):
        app = Application(aid='123456789')
        task = app.launch_task('test')
        self.assertTrue(task.get_progress() == 0)


class NotificationModelTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_naturaltime(self):
        n = Notification(name='test')
        db.session.add(n)
        db.session.commit()
        time.sleep(2)
        self.assertTrue(n.get_naturaltime() == '2 seconds ago')

    def test_get_data(self):
        json_text = '{"k1": "v1", "k2": "v2"}'
        n = Notification(payload_json=json_text)
        self.assertTrue(n.get_data() == json.loads(json_text))

    def test_get_data_with_key(self):
        json_text = '{"k1": "v1", "k2": "v2"}'
        n = Notification(payload_json=json_text)
        self.assertTrue(n.get_data(key='k2') == 'v2')

    def test_get_data_with_invalid_key(self):
        json_text = '{"k1": "v1", "k2": "v2"}'
        n = Notification(payload_json=json_text)
        self.assertTrue(n.get_data(key='k3') is None)

    def test_get_message(self):
        json_text = '{"msg": "message"}'
        n = Notification(payload_json=json_text)
        self.assertTrue(n.get_message() == 'message')

    def test_get_message_none(self):
        json_text = '{"nomsg": "message"}'
        n = Notification(payload_json=json_text)
        self.assertTrue(n.get_message() is None)
