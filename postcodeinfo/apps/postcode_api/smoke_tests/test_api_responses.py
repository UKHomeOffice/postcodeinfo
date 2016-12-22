import os

# when we move to python3.5, just use unittest
from unittest2 import TestCase

from postcode_api.smoke_tests.genuine_api import GenuineApi


class ApiResponsesTestCase(TestCase):

    def setUp(self):
        self.api = GenuineApi(root_url=os.environ.get("API_ROOT_URL"),
                              auth_token=os.environ.get('API_AUTH_TOKEN', ''))

    def assert_http_200_response_with_valid_json(self, endpoint):
        r = self.api.get(endpoint)
        self.assertEqual(200, r.status_code)
        return r.json()

    def test_that_there_is_at_least_one_address(self):
        r = self.assert_http_200_response_with_valid_json(
            '/addresses/?postcode=BS483DY')
        self.assertGreater(len(r), 0)

    def test_that_there_is_a_local_authority(self):
        r = self.assert_http_200_response_with_valid_json('/postcodes/BS483DY')
        assert r['local_authority'] is not None
        assert r['local_authority']['name']

    def test_that_the_postcode_has_a_latitude_and_longitude(self):
        r = self.assert_http_200_response_with_valid_json('/postcodes/BS483DY')
        self.assertEqual(2, len(r['centre']['coordinates']))

    def test_that_there_are_no_duplicate_uprns_for_the_same_postcode(self):
        postcode_samples = [
            "co49ux", "pe39xa", "cm36eu", "n193pr", "dh99es", "ne137nq",
            "pe46gs", "pe46de", "co63jy", "ts212je", "pe38nf", "dh96hh",
            "ts201qh", "ne32sl", "pe47dx", "bs166qs", "bs166qw", "bs45ea",
            "bs41jz", "pe129sa"
        ]
        for postcode in postcode_samples:
            with self.subTest(postcode=postcode):
                r = self.assert_http_200_response_with_valid_json(
                    '/addresses?postcode={}'.format(postcode))
                uprn_list = [item['uprn'] for item in r]
                self.assertEqual(len(uprn_list), len(set(uprn_list)))
