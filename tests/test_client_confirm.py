import time

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientUnconfirmedTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(email='john@example.com', password='S3cret!!')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_unconfirmed_page_before_login(self):
        """
        GIVEN an anonymous user (not logged in and not confirmed)
        WHEN sending an HTTP GET request to '/auth/unconfirmed'
        THEN login page is returned
        """
        response = self.client.get('/auth/unconfirmed', follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_unconfirmed_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user (not logged in and not confirmed)
        WHEN sending an HTTP POST request to '/auth/unconfirmed'
        THEN error page 405 (method not supported) is returned 
        """
        response = self.client.post('/auth/unconfirmed', follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_unconfirmed_page_after_login(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to '/auth/unconfirmed'
        THEN unconfirmed page is returned
        """
        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/unconfirmed', follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/unconfirmed.html')

    def test_unconfirmed_page_after_login_with_http_post(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP POST request to '/auth/unconfirmed'
        THEN error page 405 (method not supported) is returned
        """
        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.post('/auth/unconfirmed', follow_redirects=True)
            self.assert_405(response)
            self.assert_template_used('errors/405.html')

    def test_unconfirmed_page_after_login_with_static_asset_request(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to 
             '/static/style/bootstrap/bootstrap-4.0.0.min.css'
        THEN the requested asset is correctly returned
        """
        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get(
                '/static/style/bootstrap/bootstrap-4.0.0.min.css',
                follow_redirects=True)
            self.assert_200(response)

    def test_unconfirmed_page(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP GET request to '/auth/unconfirmed'
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/unconfirmed', follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')


class FlaskClientConfirmTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(email='john@example.com', password='S3cret!!')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_confirm_page_no_token_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/confirm'
        THEN login page is returned
        """
        response = self.client.get('/auth/confirm', follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')
        self.assert_message_flashed('Please log in to access this page.')

    def test_confirm_page_no_token_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/confirm'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post('/auth/confirm', follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_confirm_page_after_login(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to '/auth/confirm'
        THEN unconfirmed page is returned
        """
        with self.client:
            self.client.post('auth/login', data={
                'email':'john@example.com',
                'password':'S3cret!!'
            })

            response = self.client.get('/auth/confirm', follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/unconfirmed.html')
            self.assert_message_flashed('A confirmation email has been sent to you')

    def test_confirm_page_after_login_with_http_post(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP POST request to '/auth/confirm'
        THEN error page 405 (method not supported) is returned
        """
        with self.client:
            self.client.post('auth/login', data={
                'email':'john@example.com',
                'password':'S3cret!!'
            })

            response = self.client.post('/auth/confirm', follow_redirects=True)
            self.assert_405(response)
            self.assert_template_used('errors/405.html')

    def test_already_confirmed(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP GET request to '/auth/confirm'
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/confirm', follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')


class FlaskClientConfirmWithTokenTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

        u = User(email='john@example.com', password='S3cret!!')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_confirm_page_token_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/confirm' with token
        THEN login page is returned
        """
        response = self.client.get('/auth/confirm/1234567890',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')
        self.assert_message_flashed('Please log in to access this page.')

    def test_confirm_page_token_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/confirm' with token
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post('/auth/confirm/1234567890',
                                    follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_confirm_page_invalid_token(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to '/auth/confirm' with invalid token
        THEN unconfirmed page is returned 
        """
        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/confirm/1234567890',
                                       follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/unconfirmed.html')
            self.assert_message_flashed('The confirmation link in invalid or expired',
                                        category='error')

    def test_confirm_page_expired_token(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to '/auth/confirm' with expired token
        THEN unconfirmed page is returned 
        """
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_confirmation_token(expires_in=1)

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })
            time.sleep(2)

            response = self.client.get('/auth/confirm/{}'.format(token),
                                       follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/unconfirmed.html')
            self.assert_message_flashed('The confirmation link in invalid or expired',
                                        category='error')

    def test_confirm_page_token(self):
        """
        GIVEN an authenticated user but not confirmed
        WHEN sending an HTTP GET request to '/auth/confirm' with valid token
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_confirmation_token()

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/confirm/{}'.format(token),
                                       follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assert_message_flashed('You have confirmed your account. Thanks!')

    def test_confirm_page_already_confirmed(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP request to '/auth/confirm' with valid token
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        u.confirmed = True
        token = u.generate_confirmation_token()
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/confirm/{}'.format(token),
                                       follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assertTrue(len(self.flashed_messages) == 0)

    def test_confirm_page_already_confirmed_and_invalid_token(self):
        """
        GIVEN an authenticated and confirmed user
        WHEN sending an HTTP request to '/auth/confirm' with invalid token
        THEN application dashboard page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        u.confirmed = True
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            })

            response = self.client.get('/auth/confirm/1234567890',
                                       follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assertTrue(len(self.flashed_messages) == 0)
