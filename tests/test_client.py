import re

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_register_login_confirm_logout(self):
        with self.client:
            response = self.client.post('/auth/register', data={
                'username': 'john',
                'email': 'john@example.com',
                'company': 'ACME Co.',
                'password': 'S3cret!!',
                'password2': 'S3cret!!',
            })
            self.assert_redirects(response, '/auth/login')
            self.assert_message_flashed('A confirmation email has been sent to you')
    
            response = self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'S3cret!!'
            }, follow_redirects=True)
            self.assert_200(response)
            self.assertTrue(re.search('Hello,\s+john',
                                      response.get_data(as_text=True)))
    
            user = User.query.filter_by(email='john@example.com').first()
            token = user.generate_confirmation_token()
            response = self.client.get('/auth/confirm/{}'.format(token),
                                       follow_redirects=True)
            self.assert_200(response)
    
            response = self.client.get('auth/logout', follow_redirects=True)
            self.assert_200(response)
            self.assert_message_flashed('You have been logged out')
