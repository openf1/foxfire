from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientLogoutTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(email='john@example.com',
                 password='cat')
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_logout_page(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/logout'
        THEN logout page is returned
        """
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')
        self.assert_message_flashed('You have been logged out')

    def test_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/logout'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post('/auth/logout', follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_logout_authenticated(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/auth/logout'
        THEN login page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'
            }, follow_redirects=True)

            response = self.client.get('/auth/logout', follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/login.html')
            self.assert_message_flashed('You have been logged out')
