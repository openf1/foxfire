import re

from flask_testing import TestCase

from app import create_app


class FlaskClientMainTestCase(TestCase):
    def create_app(self):
        return create_app('testing')

    def test_redirect_main_page(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/'
        THEN user is redirected to 'openf1.github.io'
        """
        response = self.client.get('/', follow_redirects=False)
        self.assert_redirects(response, 'https://openf1.github.io')
