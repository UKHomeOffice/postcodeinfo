import json

from django.test import TestCase
from django.contrib.auth.models import User
from mock import patch
from rest_framework.authtoken.models import Token


class SupportViewsTestCase(TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.valid_token = 'Token ' + str(self.user.auth_token)

    # describe: ping.json
    def test_that_getting_ping_json_with_a_valid_token_produces_parseable_json(self):
        response = self.client.get(
            '/ping.json', {}, True, False, HTTP_AUTHORIZATION=self.valid_token)
        json.loads(response.content)

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
        json.loads(response.content)

    def test_that_getting_ping_json_with_and_invalid_token_responds_with_HTTP_401(self):
        response = self.client.get(
            '/ping.json', {}, True, False, HTTP_AUTHORIZATION='Token 1234')
        self.assertEqual(response.status_code, 401)

    # describe: healthcheck.json
    def test_that_getting_healthcheck_json_with_a_valid_token_produces_parseable_json(self):
        response = self.client.get(
            '/healthcheck.json', {}, True, False, HTTP_AUTHORIZATION=self.valid_token)
        json.loads(response.content)

    def test_that_when_the_database_is_ok_then_getting_healthcheck_json_with_a_valid_token_responds_with_HTTP_200(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            response = self.client.get(
                '/healthcheck.json', {}, True, False, HTTP_AUTHORIZATION=self.valid_token)
        self.assertEqual(response.status_code, 200)

    def test_that_when_the_database_is_ok_then_getting_healthcheck_json_with_no_token_responds_with_HTTP_200(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            response = self.client.get(
                '/healthcheck.json', {}, True, False)
        self.assertEqual(response.status_code, 200)

    def test_that_getting_healthcheck_json_with_no_token_produces_parseable_json(self):
        response = self.client.get(
            '/healthcheck.json', {}, True, False)
        json.loads(response.content)

    def test_that_getting_healthcheck_json_with_and_invalid_token_responds_with_HTTP_401(self):
        response = self.client.get(
            '/healthcheck.json', {}, True, False, HTTP_AUTHORIZATION='Token 1234')
        self.assertEqual(response.status_code, 401)

    def test_that_when_the_database_is_ok_it_shows_ok_true_in_the_database_element(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            response = self.client.get(
                '/healthcheck.json', {}, True, False)
        result = json.loads(response.content)
        self.assertEqual( True, result['database']['ok'] )

    def test_that_when_the_database_is_ok_it_shows_ok_true_at_the_top_level(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            response = self.client.get(
                '/healthcheck.json', {}, True, False)
        result = json.loads(response.content)
        self.assertEqual( True, result['ok'] )

    def test_that_when_the_database_is_not_ok_it_shows_ok_false_in_the_database_element(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=False):
            response = self.client.get(
                '/healthcheck.json', {}, True, False)
        result = json.loads(response.content)
        self.assertEqual( False, result['database']['ok'] )

    def test_that_when_the_database_is_not_ok_it_shows_ok_false_at_the_top_level(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=False):
            response = self.client.get(
                '/healthcheck.json', {}, True, False)
        result = json.loads(response.content)
        self.assertEqual( False, result['ok'] )
