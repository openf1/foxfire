import re

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientLoginTestCase(TestCase):
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

    def test_login_page(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/login'
        THEN login page is returned
        """
        response = self.client.get('/auth/login')
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_login_with_no_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/login' without form data
        THEN login page is returned
        """
        response = self.client.post('/auth/login')
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_login_with_missing_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/login' without password
        THEN login page is returned
        """
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com'
        })
        self.assert_200(response)
        self.assertTrue(re.search('Please enter your password',
                        response.get_data(as_text=True)))
        self.assert_template_used('auth/login.html')

    def test_login_with_missing_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/login' without email
        THEN login page is returned
        """
        response = self.client.post('/auth/login', data={
            'password': 'cat'
        })
        self.assert_200(response)
        self.assertTrue(re.search('Please enter your email address',
                        response.get_data(as_text=True)))
        self.assert_template_used('auth/login.html')

    def test_login_with_unknown_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/login' with unknown email
        THEN login page is returned
        """
        response = self.client.post('/auth/login', data={
            'email': 'dave@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assert_200(response)
        self.assert_message_flashed('Username or password was incorrect',
                                    category='error')
        self.assert_template_used('auth/login.html')

    def test_login_with_wrong_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/login' with incorrect password
        THEN login page is returned
        """
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com',
            'password': 'dog'
        }, follow_redirects=True)
        self.assert_200(response)
        self.assert_message_flashed('Username or password was incorrect',
                                    category='error')
        self.assert_template_used('auth/login.html')

    def test_login_already_authenticated(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/login'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
