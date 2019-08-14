"""Contain tests for the user endpoints."""
from flask import json
import unittest
# local imports
from api.models import db
from api.routes import app


class UserRoutesTestCase(unittest.TestCase):
    """This class represents the user routes test case."""

    def setUp(self):
        """Define test variables."""
        self.app = app
        self.client = self.app.test_client()
        self.test_user = {
            "name": "My Test Name",
            "email": "test1@testing.com",
            "username": "test1",
            "password": "123$usr"
        }
        self.test_user2 = {
            "name": "My Second Test",
            "email": "test1@testing.com",  # similar email to the previous user
            "username": "test2",
            "password": "123$usr"
        }
        self.test_user3 = {
            "name": "My Third Test",
            "email": "test3@testing.com",
            "username": "test1",  # similar username to a previous user
            "password": "123$usr"
        }
        self.test_login = {
            "username": "test1",
            "password": "123$usr"
        }
        self.test_wrong_pass = {
            "username": "test1",
            "password": "123$usrs"
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_register_user_with_correct_data(self):
        """Test user registration with all info provided."""
        self.response = self.client.post('/api/v2/auth/register',
                                         data=json.dumps(self.test_user),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("My Test Name", str(self.response.data))

    def test_register_user_with_existing_email_returns_error_msg(self):
        """Test user registration with all info provided."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.test_user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/register',
                                         data=json.dumps(self.test_user2),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("already registered!", str(self.response.data))

    def test_register_user_with_registered_username_returns_error_msg(self):
        """Test user registration with all info provided."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.test_user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/register',
                                         data=json.dumps(self.test_user3),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("not available!", str(self.response.data))

    def test_login_user_with_correct_login(self):
        """Test user login with all log in details provided."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.test_user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.test_login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("Log in successful", str(self.response.data))

    def test_login_user_with_non_existent_email(self):
        """Try to login with no user created."""
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.test_login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("Email or username provided does not match any user",
                      str(self.response.data))

    def test_login_with_incorrect_email(self):
        """Test user login with all log in details provided."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.test_user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.test_wrong_pass),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("Wrong email or username/password combination",
                      str(self.response.data))

    def test_reset_password_with_correct_token(self):
        """Test password change with a token passed into the headers."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.test_user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/get-reset-token',
                                         data=json.dumps(
                                             {"email": "test1@testing.com"}),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.response = self.client.post('/api/v2/auth/reset-password',
                                         data=json.dumps(
                                             {"new_password": "%6hjhk"}),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("Password for test1 changed successfully",
                      str(self.response.data))

    def test_reset_password_with_incorrect_token(self):
        """Test password change with a wrong token passed into the headers."""
        self.token = "a wrong token token string"
        self.response = self.client.post('/api/v2/auth/reset-password',
                                         data=json.dumps(
                                             {"new password": "%6hjhk"}),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.assertEqual(self.response.status_code, 401)
        self.assertIn("Token is invalid", str(self.response.data))

    def tearDown(self):
        """Tear down all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
