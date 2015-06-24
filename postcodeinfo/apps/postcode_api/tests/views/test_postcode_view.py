import json
import os

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


from postcode_api.importers.addressbase_basic_importer import \
    AddressBaseBasicImporter
from postcode_api.importers.postcode_gss_code_importer import \
    PostcodeGssCodeImporter
from postcode_api.importers.local_authorities_importer import \
    LocalAuthoritiesImporter


class PostcodeViewTestCase(TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.valid_token = 'Token ' + str(self.user.auth_token)

        AddressBaseBasicImporter().import_csv(
            self._sample_data_file('addressbase_basic_barnet_sample.csv'))
        PostcodeGssCodeImporter().import_postcode_gss_codes(
            self._sample_data_file('NSPL_barnet_sample.csv'))
        LocalAuthoritiesImporter().import_local_authorities(
            self._sample_data_file('local_authorities_sample.nt'))

    def request(self, path, **headers):
        token = headers.pop('token', None)
        if token is not None:
            headers['HTTP_AUTHORIZATION'] = token
        return self.client.get(path, {}, True, False, **headers)

    def assert_produces_parseable_json(self, response):
        try:
            json.loads(response.content)
        except ValueError:
            self.fail("Invalid JSON response: %s" % response.content)

    def assert_status_code(self, response, code):
        self.assertEqual(code, response.status_code)

    def _sample_data_file(self, filename):
        return os.path.join(
            os.path.dirname(__file__), '../', 'sample_data/', filename)

    def valid_postcode(self, **kwargs):
        return self.request('/postcodes/N28AS', **kwargs)

    def test_valid_postcode_and_valid_token(self):
        response = self.valid_postcode(token=self.valid_token)
        self.assert_status_code(response, 200)
        self.assert_produces_parseable_json(response)

    def test_valid_postcode_with_space_and_valid_token(self):
        response = self.request('/postcodes/N2%208AS', token=self.valid_token)
        self.assert_status_code(response, 200)

    def test_invalid_postcode_with_valid_token_HTTP_404(self):
        self.assert_status_code(
            self.request('/postcodes/MUPP37', token=self.valid_token),
            404)

    def test_valid_postcode_with_invalid_token_HTTP_401(self):
        self.assert_status_code(self.valid_postcode(token='Token 1234'), 401)

    def test_json_structure(self):
        response = self.valid_postcode(token=self.valid_token)
        parsed = json.loads(response.content)
        self.assertEqual('Barnet', parsed['local_authority']['name'])
        self.assertEqual('E09000003', parsed['local_authority']['gss_code'])
        self.assertAlmostEqual(
            51.59125130451485,
            parsed['centre']['latitude'], 4)
        self.assertAlmostEqual(
            -0.16635044363607124,
            parsed['centre']['longitude'], 4)
