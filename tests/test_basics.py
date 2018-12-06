import re

from flask import current_app
from flask_testing import TestCase

from app import create_app
from app import db
from config import config


class BasicsTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_app_dev_version(self):
        v = config['development'].version()
        self.assertTrue(
            re.match(r'\d{1,2}\.\d{1,2}\.\d{1,2}\+dev', v['version'])
        )

    def test_app_test_version(self):
        v = config['testing'].version()
        self.assertTrue(
            re.match(r'\d{1,2}\.\d{1,2}\.\d{1,2}-rc', v['version'])
        )

    def test_app_test_prod_version(self):
        v = config['production'].version()
        self.assertTrue(
            re.match(r'\d{1,2}\.\d{1,2}\.\d{1,2}', v['version'])
        )
