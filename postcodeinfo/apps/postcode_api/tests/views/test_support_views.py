import json
import os

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from postcode_api.importers.addressbase_basic_importer\
    import AddressBaseBasicImporter


class SupportViewsTestCase(TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.valid_token = 'Token ' + str(self.user.auth_token)

    def test_that_getting_ping_json_with_a_valid_token_produces_parseable_json(self):
        response = self.client.get(
            '/ping.json', {}, True, False, HTTP_AUTHORIZATION=self.valid_token)
        parsed = json.loads(response.content)
        self.assertIsInstance(parsed, dict)

    def test_that_getting_ping_json_with_a_valid_token_responds_with_HTTP_200(self):
        response = self.client.get(
            '/ping.json', {}, True, False, HTTP_AUTHORIZATION=self.valid_token)
        self.assertEqual(response.status_code, 200)

    def test_that_getting_ping_json_with_no_token_responds_with_HTTP_200(self):
        response = self.client.get(
            '/ping.json', {}, True, False)
        self.assertEqual(response.status_code, 200)

    def test_that_getting_ping_json_with_no_token_produces_parseable_json(self):
        response = self.client.get(
            '/ping.json', {}, True, False)
        parsed = json.loads(response.content)
        self.assertIsInstance(parsed, dict)

    def test_that_getting_ping_json_with_and_invalid_token_responds_with_HTTP_401(self):
        response = self.client.get(
            '/ping.json', {}, True, False, HTTP_AUTHORIZATION='Token 1234')
        self.assertEqual(response.status_code, 401)
