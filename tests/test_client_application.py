import re

from flask import current_app
from flask_testing import TestCase

from app import create_app
from app import db
from app.models import User
from app.models import Application


class FlaskClientApplicationDashboardTestCase(TestCase):
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

    def test_dashboard_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application'
        THEN login page is returned
        """
        response = self.client.get(
            '/application',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_dashboard_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/application'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')

    def test_dashboard_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post(
            '/application',
            follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_dashboard_page_after_login_with_http_post(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/application'
        THEN error page 405 (method not supported) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application',
                follow_redirects=True)
            self.assert_405(response)
            self.assert_template_used('errors/405.html')


class FlaskClientCreateApplicationTestCase(TestCase):
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

    def test_create_app_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/create'
        THEN login page is returned
        """
        response = self.client.get(
            '/application/create',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_create_app_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/create'
        THEN login page is returned
        """
        response = self.client.post(
            '/application/create',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_create_app_page_after_login(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/application/create'
        THEN create application page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/create',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/create.html')

    def test_create_app_page_after_login_no_data(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/application/create' without
             form data
        THEN create application page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/create',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/create.html')

    def test_create_app_page_after_login_no_optional_description(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/application/create' without
             optional description
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/create',
                data={'name': 'test application'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')

    def test_create_app_page_after_login_with_optional_description(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/application/create'
             with optional description
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/create',
                data={'name': 'test application',
                      'description': 'this is a test application'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')

    def test_create_app_page_after_login_existing_app(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to '/application/create'
             with existing application name
        THEN create application page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        app = Application(appname='test', owner=u)
        db.session.add(app)
        db.session.commit()

        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/create',
                data={'name': 'test'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/create.html')
            self.assertTrue(
                re.search('Please use a different application name',
                          response.get_data(as_text=True)))


class ApplicationTestCase(TestCase):
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

        app = Application(appname='test',
                          description='test application',
                          aid='1234567890',
                          owner=u)
        app.fingerprint = 'abcdef1234567890'
        app.key = 'thisisthekey'
        db.session.add(app)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class FlaskClientViewApplicationTestCase(ApplicationTestCase):
    def test_view_application_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/view'
        THEN login page is returned
        """
        response = self.client.get(
            '/application/view/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_view_application_page_app_not_found(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to 'application/view'
             with non-existing application id
        THEN application error page 404 (page not found) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/view/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_view_application_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/view/'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post(
            '/application/view/1234567890',
            follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_view_application_page(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to 'application/view'
        THEN application view page 404 is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/view/1234567890',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/view.html')


class FlaskClientEditApplicationTestCase(ApplicationTestCase):
    def test_edit_application_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/edit'
        THEN login page is returned
        """
        response = self.client.get(
            '/application/edit/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_edit_application_page_app_not_found(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to 'application/edit'
             with non-existing application id
        THEN application error page 404 (page not found) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/edit/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_edit_application_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/edit'
        THEN login page is returned
        """
        response = self.client.post(
            '/application/edit/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_edit_application_page_app_not_found_with_http_post(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/edit'
             with non-existing application id
        THEN application error page 404 (page not found) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/edit/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_edit_application_page_existing_app_name(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/edit'
             with existing application name
        THEN edit application page is returned
        """
        u = User.query.filter_by(email='john@example.com').first()
        app = Application(appname='another', owner=u)
        db.session.add(app)
        db.session.commit()

        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/edit/1234567890',
                data={'name': 'another'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/edit.html')
            self.assertTrue(re.search(
                'Please use a different application name',
                response.get_data(as_text=True)))

    def test_edit_application_page_same_app_name(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/edit'
             with same application name
        THEN application view page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/edit/1234567890',
                data={'name': 'test'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/view.html')
            self.assert_message_flashed(
                'Your application details have been successfully updated.')

    def test_edit_application_page_with_optional_description(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/edit' with
             optional description
        THEN application view page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/edit/1234567890',
                data={'name': 'another',
                      'description': 'another application'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/view.html')
            self.assert_message_flashed(
                'Your application details have been successfully updated.')

    def test_edit_application_page_without_optional_description(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/edit' without
             optional application description
        THEN application view page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/edit/1234567890',
                data={'name': 'another'},
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/view.html')
            self.assert_message_flashed(
                'Your application details have been successfully updated.')


class FlaskClientDeleteApplicationTestCase(ApplicationTestCase):
    def test_delete_application_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/delete'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.get(
            '/application/delete/1234567890',
            follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_delete_application_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/delete'
        THEN login page is returned
        """
        response = self.client.post(
            '/application/delete/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_delete_application_page_app_not_found(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/delete' with
             non-existing application id
        THEN application error page 404 (page not found) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/delete/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_delete_application_page(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/delete'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/delete/1234567890',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')
            self.assert_message_flashed('Your application has been deleted.')

        app = Application.query.filter_by(aid='1234567890').first()
        self.assertTrue(app is None)


class FlaskClientRenewApplicationTestCase(ApplicationTestCase):
    def test_renew_application_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/renew'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.get(
            '/application/renew/1234567890',
            follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_renew_application_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/renew'
        THEN login page is returned
        """
        response = self.client.post(
            '/application/renew/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_renew_application_page_app_not_found(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/renew'
             with non-existing application id
        THEN app_not_found error page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/renew/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_renew_application_page_invalid_form(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/renew'
             with empty form data
        THEN application view page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            current_app.config['WTF_CSRF_ENABLED'] = True
            response = self.client.post(
                '/application/renew/1234567890',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/view.html')

    def test_renew_application_page(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP POST request to 'application/renew'
        THEN application dashboard page is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.post(
                '/application/renew/1234567890',
                follow_redirects=True)

            self.assert_200(response)
            self.assert_template_used('application/dashboard.html')


class FlaskClientDownloadApplicationTestCase(ApplicationTestCase):
    def test_download_application_page_before_login(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP GET request to '/application/download'
        THEN login page is returned
        """
        response = self.client.get(
            '/application/download/1234567890',
            follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used('auth/login.html')

    def test_download_application_page_before_login_with_http_post(self):
        """
        GIVEN an anonymous user
        WHEN sending an HTTP POST request to '/application/download'
        THEN error page 405 (method not supported) is returned
        """
        response = self.client.post(
            '/application/download/1234567890',
            follow_redirects=True)
        self.assert_405(response)
        self.assert_template_used('errors/405.html')

    def test_download_application_page_app_not_found(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/application/download' with
             non-existing application id
        THEN application error page 404 (page not found) is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/download/0987654321',
                follow_redirects=True)
            self.assert_200(response)
            self.assert_template_used('application/errors/app_not_found.html')

    def test_download_application_page(self):
        """
        GIVEN an authenticated user
        WHEN sending an HTTP GET request to '/application/download'
        THEN pem file is returned
        """
        with self.client:
            self.client.post(
                '/auth/login',
                data={'email': 'john@example.com',
                      'password': 'cat'},
                follow_redirects=True)

            response = self.client.get(
                '/application/download/1234567890',
                follow_redirects=True)
            cd = response.headers.get('Content-Disposition')
            app = Application.query.filter_by(aid='1234567890').first()
            filename = '{}.pem'.format(app.fingerprint[0:8])

            self.assert_200(response)
            self.assertTrue(cd == 'attachment; filename={}'.format(filename))
            self.assertTrue(b'thisisthekey' == response.get_data())
