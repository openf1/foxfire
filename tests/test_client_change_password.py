import re
import time

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User


class FlaskClientChangePasswordTestCase(TestCase):
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

    def test_change_password_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/auth/change_password'
        THEN login page is returned
        """
        response = self.client.get('/auth/change_password',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_change_password_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/auth/change_password'
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.get('/auth/change_password',
                                   follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')

    def test_change_password_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/auth/change_password'
        THEN login page is returned
        """
        response = self.client.post('/auth/change_password',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_change_password_page_after_login_with_no_data(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' 
             without form data
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password',
                                        follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')

    def test_change_password_after_login_missing_current_password(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' without
             current password
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'password': 'S3cret!!',
                'password2': 'S3cret!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assertTrue(re.search('Please enter your current password',
                                      response.get_data(as_text=True)))

    def test_change_password_after_login_missing_new_password(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' without
             new password
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'old_password': 'cat',
                'password2': 'S3cret!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assertTrue(re.search(
                "Please enter a new password with a mix of numbers,"
                "uppercase and lowercase letters,"
                "and special characters", response.get_data(as_text=True)))

    def test_change_password_after_login_missing_new_password2(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' without
             new password confirmation field
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'old_password': 'cat',
                'password': 'S3cret!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assertTrue(re.search('Please confirm your new password',
                                      response.get_data(as_text=True)))

    def test_change_password_after_login_incorrect_current_password(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' with
             incorrect current password
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'old_password': 'dog',
                'password': 'S3cret!!',
                'password2': 'S3cret!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assert_message_flashed(
                'Current password could not be invalidated',
                category='error')

    def test_change_password_after_login_weak_new_password(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' with
             weak new password
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data = {
                'old_password': 'cat',
                'password': 'dog',
                'password2': 'dog'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assertTrue(re.search(
                "Please enter a new password with a mix of numbers,"
                "uppercase and lowercase letters,"
                "and special characters", response.get_data(as_text=True)))

    def test_change_password_after_login_new_password_do_not_match(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' where
             new passwords do no match
        THEN change password page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'old_password': 'cat',
                'password': 'S3cret!!',
                'password2': 'S3cret!!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/change_password.html')
            self.assertTrue(re.search('Please confirm your new password',
                                      response.get_data(as_text=True)))

    def test_change_password_after_login_valid_new_password(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/auth/change_password' with
             valid new password
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post('/auth/login', data = {
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/auth/change_password', data={
                'old_password': 'cat',
                'password': 'S3cret!!',
                'password2': 'S3cret!!'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assert_message_flashed(
                'Your password has been successfully changed.')
