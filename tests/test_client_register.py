import re

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientRegisterTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register_page(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/register'
        THEN registration page is returned
        """
        response = self.client.get('/auth/register')
        self.assert_200(response)
        self.assert_template_used('auth/register.html')

    def test_register_with_no_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             without form data
        THEN registration page is returned
        """
        response = self.client.post('/auth/register')
        self.assert_200(response)
        self.assert_template_used('auth/register.html')

    def test_register_with_missing_username_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with missing username
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'cat',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Please enter your name',
                                  response.get_data(as_text=True)))

    def test_register_with_missing_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with missing email
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'company': 'ACME Co.',
                  'password': 'cat',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Please enter an email address',
                                  response.get_data(as_text=True)))

    def test_register_with_invalid_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with invalid email
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john',
                  'company': 'ACME Co.',
                  'password': 'cat',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Please enter a valid email address',
                                  response.get_data(as_text=True)))

    def test_register_with_missing_company_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with missing company
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'password': 'cat',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(
            re.search('Please enter your organization/company name',
                      response.get_data(as_text=True)))

    def test_register_with_missing_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with missing password
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search(
            ("Please enter a strong password with a mix of numbers,"
             "uppercase and lowercase letters,and special characters"),
            response.get_data(as_text=True)))

    def test_register_with_missing_password2_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with missing password confirmation
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Passwords must match',
                                  response.get_data(as_text=True)))

    def test_register_with_incorrect_password_confirmation(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register' with password
             field that do not match
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'S3cret!!',
                  'password2': 'dog'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Passwords must match',
                                  response.get_data(as_text=True)))

    def test_register_with_weak_password_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             with weak password
        THEN registration page is returned
        """
        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'cat',
                  'password2': 'cat'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')

    def test_register_with_existing_username_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             for existing user
        THEN registration page is returned
        """
        u = User(username='john')
        db.session.add(u)
        db.session.commit()

        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'S3cret!!',
                  'password2': 'S3cret!!'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Please use a different name',
                                  response.get_data(as_text=True)))

    def test_register_with_existing_email_data(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/register'
             for existing email
        THEN registration page is returned
        """
        u = User(email='john@example.com')
        db.session.add(u)
        db.session.commit()

        response = self.client.post(
            '/auth/register',
            data={'username': 'john',
                  'email': 'john@example.com',
                  'company': 'ACME Co.',
                  'password': 'S3cret!!',
                  'password2': 'S3cret!!'})
        self.assert_200(response)
        self.assert_template_used('auth/register.html')
        self.assertTrue(re.search('Please use a different email address',
                                  response.get_data(as_text=True)))


class FlaskClientRegisterAuthenticatedTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(email='john@example.com', password='cat')
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register_with_authenticated_user(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP POST request to '/auth/register'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'})

            response = self.client.get(
                '/auth/register',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
