import json, os

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from postcode_api.importers.addressbase_basic_importer import AddressBaseBasicImporter

class AddressViewTestCase(TestCase):
  def setUp(self):
    self.user = User()
    self.user.save()
    token = Token.objects.create(user=self.user)
    token.save()
    self.valid_token = 'Token ' + str(self.user.auth_token)
    self._import_data_from('addressbase_basic_sample.csv')
    
  def _sample_data_file(self, filename):
    return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

  def _import_data_from(self, file):
    return AddressBaseBasicImporter().import_csv(self._sample_data_file(file))

  def test_that_getting_addresses_with_a_valid_postcode_and_token_produces_parseable_json(self):
    response = self.client.get('/addresses/', {'postcode': 'EX68BP'}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    parsed = json.loads(response.content) 
    self.assertIsInstance(parsed, list)

  def test_that_getting_addresses_with_a_valid_postcode_and_token_responds_with_HTTP_200(self):
    response = self.client.get('/addresses/', {'postcode': 'EX68BP'}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    self.assertEqual(response.status_code, 200)

  def test_that_getting_addresses_with_an_invalid_postcode_and_valid_token_responds_with_HTTP_200_and_empty_array(self):
    response = self.client.get('/addresses/', {'postcode': 'ZYX123'}, True, False, HTTP_AUTHORIZATION=self.valid_token )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, '[]')

  def test_that_getting_addresses_with_a_valid_postcode_and_invalid_token_responds_with_HTTP_401(self):
    response = self.client.get('/addresses/', {'postcode': 'EX68BP'}, True, False, HTTP_AUTHORIZATION='Token 1234' )
    self.assertEqual(response.status_code, 401)