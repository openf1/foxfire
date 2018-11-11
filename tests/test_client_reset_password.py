import re
import time

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientResetPasswordRequestTestCase(TestCase):
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

    def test_reset_password_request_page(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/reset_password_request'
        THEN reset password request page is returned
        """
        response = self.client.get(
            '/auth/reset_password_request',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password_request.html')

    def test_reset_with_no_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password_request'
             without form data
        THEN reset password request page is returned
        """
        response = self.client.post(
            '/auth/reset_password_request',
            follow_redirects=True)
        self.assert_200(response)
        self.assertTrue(re.search('Please enter an email address',
                        response.get_data(as_text=True)))
        self.assert_template_used('auth/reset_password_request.html')

    def test_reset_with_invalid_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password_request'
             with invalid email
        THEN reset password request page is returned
        """
        response = self.client.post(
            '/auth/reset_password_request',
            data={'email': 'john'},
            follow_redirects=True)
        self.assert_200(response)
        self.assertTrue(re.search('Please enter a valid email address',
                        response.get_data(as_text=True)))
        self.assert_template_used('auth/reset_password_request.html')

    def test_reset_with_unknown_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password_request'
             with unknown email
        THEN login page is returned
        """
        response = self.client.post(
            '/auth/reset_password_request',
            data={'email': 'dave@example.com'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_reset_with_known_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password_request'
             with known email
        THEN login page is returned
        """
        response = self.client.post(
            '/auth/reset_password_request',
            data={'email': 'john@example.com'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_message_flashed(
            'Check your email for the instructions to reset your password')
        self.assert_template_used('auth/login.html')

    def test_reset_with_authenticated_user(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/reset_password_request'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/auth/reset_password_request',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')


class FlaskClientResetPasswordTestCase(TestCase):
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

    def test_reset_password_page_without_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/reset_password'
             without token
        THEN error page 404 (page not found) is returned
        """
        response = self.client.get(
            '/auth/reset_password',
            follow_redirects=True)
        self.assert_404(response)
        self.assert_template_used('errors/404.html')

    def test_reset_password_page_with_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/reset_password' with token
        THEN reset password page is returned
        """
        response = self.client.get(
            '/auth/reset_password/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')

    def test_reset_no_data_no_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             without form data and without token
        THEN error page 404 (page not found) is returned
        """
        response = self.client.post(
            '/auth/reset_password',
            follow_redirects=True)
        self.assert_404(response)
        self.assert_template_used('errors/404.html')

    def test_reset_no_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             without form data and with token
        THEN reset password page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')

    def test_reset_missing_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             without password and with token
        THEN reset pasword page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            data={'password2': 'S3cret!!'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')
        self.assertTrue(re.search(
            ("Please enter a strong password with a mix of numbers,"
             "uppercase and lowercase letters,and special characters"),
            response.get_data(as_text=True)))

    def test_reset_missing_password2_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             without password confirmation and with token
        THEN reset pasword page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            data={'password': 'S3cret!!'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')
        self.assertTrue(re.search('Passwords must match',
                                  response.get_data(as_text=True)))

    def test_reset_passwords_do_not_match(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             with password confirmation that do not match password
             field and with token
        THEN reset pasword page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            data={'password': 'S3cret!!',
                  'password2': 'dog'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')
        self.assertTrue(re.search('Passwords must match',
                                  response.get_data(as_text=True)))

    def test_reset_weak_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password' with weak
             password and with token
        THEN reset pasword page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            data={'password': 'dog',
                  'password2': 'dog'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/reset_password.html')
        self.assertTrue(re.search(
            ("Please enter a strong password with a mix of numbers,"
             "uppercase and lowercase letters,and special characters"),
            response.get_data(as_text=True)))

    def test_reset_invalid_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             with invalid token
        THEN login page is returned
        """
        response = self.client.post(
            '/auth/reset_password/1234567890',
            data={'password': 'S3cret!!',
                  'password2': 'S3cret!!'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_reset_expired_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             with expired token
        THEN login page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_reset_token(expires_in=1)

        time.sleep(2)
        response = self.client.post(
            '/auth/reset_password/{}'.format(token),
            data={'password': 'S3cret!!',
                  'password2': 'S3cret!!'},
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_reset_password_authenticated_user(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             with valid token
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_reset_token()

        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/auth/reset_password/{}'.format(token),
                data={'password': 'S3cret!!',
                      'password2': 'S3cret!!'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assertTrue(len(self.flashed_messages) == 0)

    def test_reset_password_authenticated_user_invalid_token(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP POST request to '/auth/reset_password'
             with invalid token
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/auth/reset_password/1234567890',
                data={'password': 'S3cret!!',
                      'password2': 'S3cret!!'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assertTrue(len(self.flashed_messages) == 0)

    def test_reset_password_valid_token(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/reset_password' with valid
             password and token
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_reset_token()

        with self.client:
            response = self.client.post(
                '/auth/reset_password/{}'.format(token),
                data={'password': 'S3cret!!',
                      'password2': 'S3cret!!'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/login.html')
            self.assert_message_flashed('Your password has been reset')

            response = self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'S3cret!!'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
