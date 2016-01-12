import os

from django.test import TestCase

from postcode_api.models import LocalAuthority
from postcode_api.importers.local_authorities_importer \
    import LocalAuthoritiesImporter


ROWS_IN_SAMPLE_DATA_FILE = 19


class LocalAuthoritiesImporterTestCase(TestCase):

    def _sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), '../',
                            'sample_data/', filename)

    def _importer(self):
        return LocalAuthoritiesImporter()

    def _import_data_from(self, file):
        self._importer().import_local_authorities(
            self._sample_data_file(file))

    def test_that_local_authority_objects_get_the_right_attributes(self):
        self._import_data_from('local_authorities_sample.csv')
        la = LocalAuthority.objects.filter(gss_code='E09000016').first()
        self.assertEqual(la.name, 'Havering')

    def test_that_existing_local_authorities_are_deleted_before_importing(self):
        LocalAuthority(gss_code='test', name='Test').save()
        self._import_data_from('local_authorities_sample.csv')
        self.assertEqual(
            LocalAuthority.objects.count(),
            ROWS_IN_SAMPLE_DATA_FILE)

