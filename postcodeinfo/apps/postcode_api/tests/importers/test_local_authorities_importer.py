import os

from django.test import TestCase

from postcode_api.models import LocalAuthority
from postcode_api.importers.local_authorities_importer import LocalAuthoritiesImporter

ROWS_IN_SAMPLE_DATA_FILE = 7;

class LocalAuthoritiesImporterTestCase(TestCase):

    def _sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

    def _importer(self):
        return LocalAuthoritiesImporter()

    def _import_data_from(self, file):
        self._importer().import_local_authorities(
            self._sample_data_file(file))

    def test_that_local_authority_objects_get_the_right_attributes(self):
        self._import_data_from('local_authorities_sample.nt')
        la = LocalAuthority.objects.filter(gss_code='E07000170').first()
        self.assertEqual(la.name, 'Ashfield')

    def test_that_when_new_local_authorities_are_imported_then_local_authority_records_get_created(self):
        # setup
        initial_la_count = LocalAuthority.objects.count()
        self._import_data_from('local_authorities_sample.nt')
        # expectation
        self.assertEqual(LocalAuthority.objects.count(), initial_la_count + ROWS_IN_SAMPLE_DATA_FILE)

    def test_that_when_existing_local_authorities_are_imported_then_duplicate_local_authority_records_dont_get_created(self):
        # setup
        initial_la_count = LocalAuthority.objects.count()
        self._import_data_from('local_authorities_sample.nt')
        self.assertEqual(LocalAuthority.objects.count(), initial_la_count + ROWS_IN_SAMPLE_DATA_FILE)
        self._import_data_from('local_authorities_sample.nt')
        # expectation
        self.assertEqual(LocalAuthority.objects.count(), initial_la_count + ROWS_IN_SAMPLE_DATA_FILE)
