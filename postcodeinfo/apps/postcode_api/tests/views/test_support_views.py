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

    def request(self, path, token=None):
        headers = {}
        if token is not None:
            headers['HTTP_AUTHORIZATION'] = token
        return self.client.get(path, {}, True, False, **headers)

    def healthcheck(self, **kwargs):
        return self.request('/healthcheck.json', **kwargs)
    
    def ping(self, **kwargs):
        return self.request('/ping.json', **kwargs)


    def assert_produces_parseable_json(self, response):
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Invalid JSON response: %s" % response.content)

    def assert_responds_with_status(self, response, status):
        self.assertEqual(status, response.status_code)

    def assert_check_ok_value(self, response, ok=True):
        self.assertEqual(ok, json.loads(response.content)['ok'] )

    def assert_database_ok_value(self, response, ok=True):
        self.assertEqual(ok, json.loads(response.content)['database']['ok'] )

    # describe: ping.json
    def test_that_getting_ping_json_with_a_valid_token_produces_parseable_json(self):
        self.assert_produces_parseable_json(self.ping(token=self.valid_token))

    def test_that_getting_ping_json_with_a_valid_token_responds_with_HTTP_200(self):
        self.assert_responds_with_status( self.ping(token=self.valid_token), 200 )

    def test_that_getting_ping_json_with_no_token_responds_with_HTTP_200(self):
        self.assert_responds_with_status( self.ping(), 200 )

    def test_that_getting_ping_json_with_no_token_produces_parseable_json(self):
        self.assert_produces_parseable_json(self.ping())

    def test_that_getting_ping_json_with_and_invalid_token_responds_with_HTTP_401(self):
        self.assert_responds_with_status( self.ping(token='Token 1234'), 401 )

    # describe: healthcheck.json
    def test_that_getting_healthcheck_json_with_a_valid_token_produces_parseable_json(self):
        self.assert_produces_parseable_json(self.healthcheck(token=self.valid_token))

    def test_that_when_the_database_is_ok_then_getting_healthcheck_json_with_a_valid_token_responds_with_HTTP_200(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            self.assert_responds_with_status( self.healthcheck(token=self.valid_token), 200 )

    def test_that_when_the_database_is_ok_then_getting_healthcheck_json_with_no_token_responds_with_HTTP_200(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            self.assert_responds_with_status( self.healthcheck(), 200 )

    def test_that_getting_healthcheck_json_with_no_token_produces_parseable_json(self):
        self.assert_produces_parseable_json(self.healthcheck())

    def test_that_getting_healthcheck_json_with_and_invalid_token_responds_with_HTTP_401(self):
        self.assert_responds_with_status( self.healthcheck(token='Token 1234'), 401 )

    def test_that_when_the_database_is_ok_it_shows_ok_true_in_the_database_element(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            self.assert_database_ok_value(self.healthcheck(token=self.valid_token), True)

    def test_that_when_the_database_is_ok_it_shows_ok_true_at_the_top_level(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=True):
            self.assert_check_ok_value(self.healthcheck(token=self.valid_token), True)

    def test_that_when_the_database_is_not_ok_it_shows_ok_false_in_the_database_element(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=False):
            self.assert_database_ok_value(self.healthcheck(token=self.valid_token), False)

    def test_that_when_the_database_is_not_ok_it_shows_ok_false_at_the_top_level(self):
        with patch('postcode_api.views.HealthcheckDotJsonView.is_database_ok', return_value=False):
            self.assert_check_ok_value(self.healthcheck(token=self.valid_token), False)

