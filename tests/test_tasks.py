from flask_testing import TestCase
from mock import patch

from app import create_app
from app import db
from app import tasks
from app.models import Application
from app.models import User


class TaskTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        app1 = Application(aid='123456789')
        db.session.add(app1)

        app2 = Application(
            aid='987654321',
            pubkey='azerty',
            key='pkazerty',
            fingerprint='fpazerty')
        db.session.add(app2)

        u = User(email='john@example.com')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch('time.sleep', return_value=None)
    def test_gen_app_key(self, mock_sleep):
        app = Application.query.filter_by(aid='123456789').first()
        u = User.query.filter_by(email='john@example.com').first()
        tasks.gen_app_key(app.id, u.id)

        self.assertTrue(app.pubkey is not None)
        self.assertTrue(app.key is not None)
        self.assertTrue(app.fingerprint is not None)
        self.assertTrue(len(u.get_notifications()) == 1)

    @patch('time.sleep', return_value=None)
    def test_renew_app_key(self, mock_sleep):
        app = Application.query.filter_by(aid='987654321').first()
        u = User.query.filter_by(email='john@example.com').first()
        tasks.renew_app_key(app.id, u.id)

        self.assertTrue(app.pubkey != 'azerty')
        self.assertTrue(app.key != 'pkazerty')
        self.assertTrue(app.fingerprint != 'fpazerty')
        self.assertTrue(len(u.get_notifications()) == 1)
