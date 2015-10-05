import json
import os

from django.test import TransactionTestCase
from django.contrib.auth.models import User
from postcode_api.models import Address

from rest_framework.authtoken.models import Token

from postcode_api.importers.addressbase_basic_importer import \
    AddressBaseBasicImporter
from postcode_api.importers.countries_importer import \
    CountriesImporter
from postcode_api.importers.postcode_gss_code_importer import \
    PostcodeGssCodeImporter
from postcode_api.importers.local_authorities_importer import \
    LocalAuthoritiesImporter


class PostcodeViewTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User()
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.valid_token = 'Token ' + str(self.user.auth_token)

        CountriesImporter().import_csv(
            self._sample_data_file('countries.csv'))
        AddressBaseBasicImporter().import_csv(
            self._sample_data_file('addressbase_basic_barnet_sample.csv'))
        PostcodeGssCodeImporter().import_postcode_gss_codes(
            self._sample_data_file('NSPL_MAY_2015_Barnet_Sample.csv'))
        LocalAuthoritiesImporter().import_local_authorities(
            self._sample_data_file('local_authorities_sample.nt'))

    def tearDown(self):
        Address.objects.all().delete()

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

    def assert_json_structure(self, response):
        parsed = json.loads(response.content)
        # local authority
        self.assertEqual('Barnet', parsed['local_authority']['name'])
        self.assertEqual('E09000003', parsed['local_authority']['gss_code'])

        lon, lat = parsed['centre']['coordinates']
        self.assertAlmostEqual(51.59124066, lat)
        self.assertAlmostEqual(-0.16658663, lon)

    def assert_has_country(self, response):
        parsed = json.loads(response.content)
        # country
        self.assertEqual('England', parsed['country']['name'])
        self.assertEqual('E92000001', parsed['country']['gss_code'])


def valid_token(url):

    def response(self):
        return self.request(url, token=self.valid_token)

    return response


def invalid_token(url):

    def response(self):
        return self.request(url, token='Token 1234')

    return response


def status_code(code):

    def assertion(self, response):
        self.assert_status_code(response, code)

    return assertion


def json_ok(self, response):
    self.assert_produces_parseable_json(response)
    self.assert_json_structure(response)


def has_country(self, response):
    self.assert_has_country(response)


def postcode(pcode):
    return '/postcodes/%s' % pcode


def partial(postcode):
    return '/postcodes/partial/%s' % postcode


cases = {

    # full postcodes
    'test_valid_postcode_and_valid_token': {
        'view': valid_token(postcode('N28AS')),
        'assert': [status_code(200), json_ok, has_country]},

    'test_valid_postcode_with_space_and_valid_token': {
        'view': valid_token(postcode('N2%208AS')),
        'assert': [status_code(200), json_ok, has_country]},

    'test_invalid_postcode_with_valid_token': {
        'view': valid_token(postcode('MUPP37')),
        'assert': [status_code(404)]},

    'test_valid_postcode_and_invalid_token': {
        'view': invalid_token(postcode('N28AS')),
        'assert': [status_code(401)]},

    # partial postcodes
    'test_valid_partial_postcode_valid_token': {
        'view': valid_token(partial('N2')),
        'assert': [status_code(200), json_ok]},

    'test_invalid_partial_postcode_valid_token_HTTP_404': {
        'view': valid_token(partial('N2MUPP37')),
        'assert': [status_code(404)]},

    'test_valid_partial_postcode_invalid_token_HTTP_401': {
        'view': invalid_token(partial('N2')),
        'assert': [status_code(401)]}
}


def make_test(case):
    view = case['view']
    assertions = case['assert']

    def case_test(self):
        response = view(self)
        for assertion in assertions:
            assertion(self, response)

    return case_test


for name, case in cases.iteritems():
    setattr(PostcodeViewTestCase, name, make_test(case))
