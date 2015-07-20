import os

from django.test import TestCase

from postcode_api.smoke_tests.genuine_api import GenuineApi


class MonitoringTestCase(TestCase):

    def setUp(self):
        self.api = GenuineApi(root_url=os.environ.get("API_ROOT_URL"),
                              auth_token=os.environ.get('API_AUTH_TOKEN', ''))

    def _make_request(self, endpoint):
        r = self.api.get(endpoint)
        self.assertEqual(200, r.status_code)
        return r.json()

    def test_that_ping_dot_json_is_ok(self):
        self._make_request('/ping.json')

    def test_that_healthcheck_dot_json_is_ok(self):
        self._make_request('/healthcheck.json')
