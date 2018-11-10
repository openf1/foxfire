import time

from datetime import datetime
from flask_testing import TestCase

from app import create_app
from app import db
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
