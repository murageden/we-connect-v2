"""Contain tests for the user endpoints."""
from flask import json
import unittest
# local imports
from api.models import db
from api.routes import app


class BusinessRoutesTestCase(unittest.TestCase):
    """This class represents the business routes test case."""

    def setUp(self):
        """Define test variables."""
        self.app = app
        self.client = self.app.test_client()
        # for registering a user
        self.user = {
            "name": "My Test Name",
            "email": "test1@testing.com",
            "username": "test1",
            "password": "123$usr"
        }
        # for logging in a user
        self.login = {
            "username": "test1",
            "password": "123$usr"
        }
        # for registering a bs
        self.test_bs = {
            "name": "Keroro Shop",
            "category": "shop",
            "description": "The best prices in town",
            "location": "Near TRM"
        }
        # for registering a bs
        self.another_test_bs = {
            "name": "Maziwa Butchery",
            "category": "shop",
            "description": "Holiday shopping ongoing, enjoy discounts",
            "location": "Near TRM"
        }
        self.wrong_test_bs = {
            "name": "  ",
            "category": "shop",
            "description": "The best prices in town",
            "location": "Near TRM"
        }
        # for modifying a bs
        self.test_update_bs = {
            "name": "Updated Test Business",
            "category": "supermarket",
            "description": "Ultimate value for money",
            "location": "Near TRM"
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_register_business_endpoint_without_token(self):
        """Trying to register a business without a token."""
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.test_bs),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.assertEqual(self.response.status_code, 401)
        self.assertIn("Token is missing", str(self.response.data))

    def test_register_business_with_correct_token_and_data(self):
        """Register a business with all input required."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.test_bs),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("The best prices in town",
                      str(self.response.data))

    def test_register_business_with_wrong_data(self):
        """Try to register a business with empty name."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.wrong_test_bs),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("Empty name is not allowed",
                      str(self.response.data))

    def test_register_business_with_a_wrong_token(self):
        """Try to register a business while supplying an incorrect token."""
        self.token = "a wrong token string"
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.test_bs),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.assertEqual(self.response.status_code, 401)
        self.assertIn("Token is invalid", str(self.response.data))

    def test_try_to_update_a_bs_with_non_existing_business_id(self):
        """Try to update a bs with token and all the details."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.test_bs),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.response = self.client.put('/api/v2/businesses/1000',
                                        data=json.dumps(self.test_update_bs),
                                        headers={
                                            'content-type': 'application/json',
                                            'x-access-token': self.token
                                        })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("Business id is incorrect",
                      str(self.response.data))

    def test_update_bs_with_correct_data_and_token(self):
        """Try to update a bs with token and all the details."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.response = self.client.post('/api/v2/businesses',
                                         data=json.dumps(self.test_bs),
                                         headers={
                                             'content-type':
                                             'application/json',
                                             'x-access-token': self.token
                                         })
        self.response = self.client.put('/api/v2/businesses/1',
                                        data=json.dumps(self.test_update_bs),
                                        headers={
                                            'content-type': 'application/json',
                                            'x-access-token': self.token
                                        })
        self.assertEqual(self.response.status_code, 201)
        self.assertIn("Ultimate value for money",
                      str(self.response.data))

    def test_delete_business_with_non_existing_business_id(self):
        """Try to delete a business with the correct token and wrong id."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.test_bs),
                         headers={
                             'content-type': 'application/json',
                             'x-access-token': self.token
                         })
        self.response = self.client.delete('/api/v2/businesses/1000',
                                           data=json.dumps(
                                               self.test_update_bs),
                                           headers={
                                               'content-type':
                                               'application/json',
                                               'x-access-token': self.token
                                           })
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("Business id is incorrect",
                      str(self.response.data))

    def test_delete_business_with_correct_token(self):
        """Try to delete a business with the correct token."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.test_bs),
                         headers={
                             'content-type': 'application/json',
                             'x-access-token': self.token
                         })
        self.response = self.client.delete('/api/v2/businesses/1',
                                           data=json.dumps(
                                               self.test_update_bs),
                                           headers={
                                               'content-type':
                                               'application/json',
                                               'x-access-token': self.token
                                           })
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("The best prices in town",
                      str(self.response.data))
        self.bs_resp = self.client.get('/api/v2/businesses/1')
        self.assertEqual(self.bs_resp.status_code, 400)
        self.assertIn("Business id is incorrect",
                      str(self.bs_resp.data))

    def test_retrieving_businesses_when_no_business_has_been_registered(self):
        """Retrieving business with no business registered."""
        self.response = self.client.get('/api/v2/businesses/search')
        self.assertEqual(self.response.status_code, 400)
        self.assertIn("No businesses yet", str(self.response.data))

    def test_retrieving_a_single_business_by_its_id_returns_the_business(self):
        """Retrieve an existing business using its id."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.test_bs),
                         headers={
                             'content-type': 'application/json',
                             'x-access-token': self.token
                         })
        self.response = self.client.get('/api/v2/businesses/1')
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("The best prices in town",
                      str(self.response.data))

    def test_retrieving_all_business_returns_all_businesses(self):
        """Retrieve a list of all registered businesses."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.test_bs),
                         headers={
                             'content-type': 'application/json',
                                             'x-access-token': self.token
                         })
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.another_test_bs),
                         headers={
                             'content-type': 'application/json',
                                             'x-access-token': self.token
                         })
        self.response = self.client.get('/api/v2/businesses/search')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(json.loads(self.response.data)['businesses']), 2)

    def test_search_businesses(self):
        """Retrieve a list of registered businesses through search."""
        self.client.post('/api/v2/auth/register',
                         data=json.dumps(self.user),
                         headers={
                             'content-type': 'application/json'
                         })
        self.response = self.client.post('/api/v2/auth/login',
                                         data=json.dumps(self.login),
                                         headers={
                                             'content-type': 'application/json'
                                         })
        self.token = json.loads(self.response.data)['token']  # grab the token
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.test_bs),
                         headers={
                             'content-type': 'application/json',
                                             'x-access-token': self.token
                         })
        self.client.post('/api/v2/businesses',
                         data=json.dumps(self.another_test_bs),
                         headers={
                             'content-type': 'application/json',
                                             'x-access-token': self.token
                         })
        self.response = self.client.get(
            '/api/v2/businesses/search?q=Keroro&location=Near TRM&category=shop')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(json.loads(self.response.data)['businesses']), 1)

    def tearDown(self):
        """Tear down all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
