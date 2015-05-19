import json, os

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


from postcode_api.importers.addressbase_basic_importer import AddressBaseBasicImporter
from postcode_api.importers.postcode_gss_code_importer import PostcodeGssCodeImporter
from postcode_api.importers.local_authorities_importer import LocalAuthoritiesImporter

class PostcodeViewTestCase(TestCase):
  def setUp(self):
    self.user = User()
    self.user.save()
    token = Token.objects.create(user=self.user)
    token.save()
    self.valid_token = 'Token ' + str(self.user.auth_token)

    AddressBaseBasicImporter().import_csv(self.__sample_data_file('addressbase_basic_barnet_sample.csv'))
    PostcodeGssCodeImporter().import_postcode_gss_codes(self.__sample_data_file('NSPL_barnet_sample.csv'))
    LocalAuthoritiesImporter().import_local_authorities(self.__sample_data_file('local_authorities_sample.nt'))
    
  def __sample_data_file(self, filename):
    return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)


  def test_that_getting_a_valid_postcode_with_a_valid_token_produces_parseable_json(self):
    response = self.client.get('/postcodes/N28AS', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    parsed = json.loads(response.content) 
    self.assertIsInstance(parsed, dict)

  def test_that_getting_a_valid_postcode_with_a_valid_token_responds_with_HTTP_200(self):
    response = self.client.get('/postcodes/N28AS', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    self.assertEqual(response.status_code, 200)

  def test_that_getting_a_valid_postcode_with_a_space_in_and_a_valid_token_responds_with_HTTP_200(self):
    response = self.client.get('/postcodes/N2%208AS', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    self.assertEqual(response.status_code, 200)

  def test_that_getting_an_invalid_postcode_with_a_valid_token_responds_with_HTTP_404(self):
    response = self.client.get('/postcodes/MUPP37', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    self.assertEqual(response.status_code, 404)

  def test_that_getting_a_valid_postcode_with_an_invalid_token_responds_with_HTTP_401(self):
    response = self.client.get('/postcodes/N28AS', {}, True, False, HTTP_AUTHORIZATION='Token 1234' )
    self.assertEqual(response.status_code, 401)

  def test_that_response_json_contains_local_authority_name_and_gss_code(self):
    response = self.client.get('/postcodes/N28AS', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    parsed = json.loads(response.content)
    self.assertEqual('Barnet', parsed['local_authority']['name'])
    self.assertEqual('E09000003', parsed['local_authority']['gss_code'])

  def test_that_response_json_contains_latitude_and_longitude_of_centre(self):
    response = self.client.get('/postcodes/N28AS', {}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    parsed = json.loads(response.content)
    self.assertAlmostEqual(51.59125130451485, parsed['centre']['latitude'], 4)
    self.assertAlmostEqual(-0.16635044363607124,  parsed['centre']['longitude'], 4)