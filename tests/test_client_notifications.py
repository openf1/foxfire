import re

from flask import current_app
from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User
from app.models import Application


class FlaskClientNotificationTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(username='john',
                 company='mycorp',
                 email='john@example.com',
                 password='cat')
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_notifications_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/notifications'
        THEN login page is returned
        """
        response = self.client.get(
            '/notifications', follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_notifications_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/notifications'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get('/notifications')
            self.assert_200(response)
            self.assertEqual(response.json, [])

    def test_reset_notifications_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/notifications/reset'
        THEN login page is returned
        """
        response = self.client.get(
            '/notifications/reset', follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_reset_notifications_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/notifications/reset'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get('/notifications/reset')
            self.assert_200(response)
            self.assertEqual(response.json, dict())

