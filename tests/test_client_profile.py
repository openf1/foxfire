import re
import time

from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User
from app.models import Application


class FlaskClientEditProfileTestCase(TestCase):
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

    def test_edit_profile_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/account/edit'
        THEN login page is returned
        """
        response = self.client.get('/account/edit',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_edit_profile_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/account/edit'
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.get('/account/edit',
                                   follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')

    def test_edit_profile_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/account/edit'
        THEN login page is returned
        """
        response = self.client.post('/account/edit',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_edit_profile_page_after_login_with_no_data_keep_current(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
             without form data (keep current)
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit',
                                        follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='john@example.com').first()
        self.assertTrue(u.username == 'john')
        self.assertTrue(u.company == 'mycorp')

    def test_client_edit_profile_page_missing_username_keep_current(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
             without username (keep current)
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'email': 'dave@example.com',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='dave@example.com').first()
        self.assertTrue(u.username == 'john')
        self.assertTrue(u.company == 'ACME Co.')

    def test_client_edit_profile_page_missing_email_keep_current(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
             without email (keep current)
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'dave',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='john@example.com').first()
        self.assertTrue(u.username == 'dave')
        self.assertTrue(u.company == 'ACME Co.')

    def test_client_edit_profile_page_missing_company_keep_current(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
             without company (keep current)
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'dave',
                'email': 'dave@example.com'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='dave@example.com').first()
        self.assertTrue(u.username == 'dave')
        self.assertTrue(u.company == 'mycorp')

    def test_client_edit_profile_page_invalid_email(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
             with invalid email
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'dave',
                'email': 'dave',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assertTrue(re.search('Please enter a valid email address',
                            response.get_data(as_text=True)))

    def test_client_edit_profile_page_no_change(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit'
             with same username and email
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'john',
                'email': 'john@example.com',
                'company': 'mycorp'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='john@example.com').first()
        self.assertTrue(u.username == 'john')
        self.assertTrue(u.company == 'mycorp')

    def test_client_edit_profile_page_existing_email(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit'
             with existing email
        THEN edit profile page is returned
        """
        u = User(email='dave@example.com')
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'john',
                'email': 'dave@example.com',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assertTrue(re.search('Please use a different email address',
                            response.get_data(as_text=True)))

    def test_client_edit_profile_page_existing_username(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit'
             with existing username
        THEN edit profile page is returned
        """
        u = User(username='dave')
        db.session.add(u)
        db.session.commit()

        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'dave',
                'email': 'john@example.com',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assertTrue(re.search('Please use a different name',
                            response.get_data(as_text=True)))

    def test_client_edit_profile_page(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/edit' 
        THEN edit profile page is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/edit', data={
                'username': 'dave',
                'email': 'dave@example.com',
                'company': 'ACME Co.'}, follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('account/edit.html')
            self.assert_message_flashed('Your profile has been successfully updated.')

        u = User.query.filter_by(email='dave@example.com').first()
        self.assertTrue(u.company == 'ACME Co.')
        self.assertTrue(u.username == 'dave')

class FlaskClientDeleteProfileTestCase(TestCase):
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

    def test_delete_profile_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/account/delete'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.get('/account/delete',
                                   follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_delete_profile_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/account/delete'
        THEN error page 405 (method not supported) is returned
        """
        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.get('/account/delete',
                                   follow_redirects=True)
            self.assert_405(response)
            self.assert_template_used('errors/405.html')

    def test_delete_profile_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/account/delete'
        THEN login page is returned
        """
        response = self.client.post('/account/delete',
                                   follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_delete_profile_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/account/delete' 
             without form data
        THEN edit profile page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        user_id = u.id

        with self.client:
            self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'cat'}, follow_redirects=True)

            response = self.client.post('/account/delete',
                                        follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('auth/register.html')
            self.assert_message_flashed('Your account has been deleted.')

            u = User.query.filter_by(email='john@example.com').first()
            self.assertTrue(u == None)
            apps = Application.query.filter_by(user_id=user_id).all()
            self.assertTrue(len(apps) == 0)
