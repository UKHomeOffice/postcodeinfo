import re
import os

from django.test import TestCase

from postcode_api.models import Address, PostcodeGssCode, LocalAuthority
from postcode_api.importers.local_authorities_importer import LocalAuthoritiesImporter



class LocalAuthoritiesImporterTestCase(TestCase):
  def __sample_data_file(self, filename):
    return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

  def __importer(self):
    return LocalAuthoritiesImporter()

  def __import_data_from(self, file):
    self.__importer().import_local_authorities(self.__sample_data_file(file))

  def test_that_local_authority_objects_get_the_right_attributes(self):
    self.__import_data_from('local_authorities_sample.nt')
    la = LocalAuthority.objects.filter(gss_code='E07000170').first()
    self.assertEqual(la.name, 'Ashfield')

  def test_that_when_new_local_authorities_are_imported_then_local_authority_records_get_created(self):
    # setup
    self.assertEqual(LocalAuthority.objects.count(), 0)
    self.__import_data_from('local_authorities_sample.nt')
    # expectation
    self.assertEqual(LocalAuthority.objects.count(), 7)

  def test_that_when_existing_local_authorities_are_imported_then_duplicate_local_authority_records_dont_get_created(self):
    # setup
    self.__import_data_from('local_authorities_sample.nt')
    self.assertEqual(LocalAuthority.objects.count(), 7)
    self.__import_data_from('local_authorities_sample.nt')
    # expectation
    self.assertEqual(LocalAuthority.objects.count(), 7)




