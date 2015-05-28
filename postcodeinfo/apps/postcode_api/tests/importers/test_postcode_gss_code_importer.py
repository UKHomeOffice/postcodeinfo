import re
import os

from django.test import TestCase

from postcode_api.models import PostcodeGssCode
from postcode_api.importers.postcode_gss_code_importer import PostcodeGssCodeImporter


class PostcodeGssCodeImporterTestCase(TestCase):

    def _sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

    def _importer(self):
        return PostcodeGssCodeImporter()

    def _import_data_from(self, file):
        self._importer().import_postcode_gss_codes(
            self._sample_data_file(file))

    def test_that_postcode_gss_code_objects_get_the_right_attributes(self):
        self._import_data_from('NSPL_sample.csv')
        postcode_gss_code = PostcodeGssCode.objects.filter(
            postcode_index='ab10ad').first()
        self.assertEqual(
            postcode_gss_code.local_authority_gss_code, 'S12000033')

    def test_that_when_new_postcode_gss_codes_are_imported_then_postcode_gss_code_records_get_created(self):
        # setup
        self.assertEqual(PostcodeGssCode.objects.count(), 0)
        self._import_data_from('NSPL_sample.csv')
        # expectation
        self.assertEqual(PostcodeGssCode.objects.count(), 9)

    def test_that_when_existing_postcode_gss_codes_are_imported_then_duplicate_postcode_gss_code_records_dont_get_created(self):
        # setup
        self._import_data_from('NSPL_sample.csv')
        self.assertEqual(PostcodeGssCode.objects.count(), 9)
        self._import_data_from('NSPL_sample.csv')
        # expectation
        self.assertEqual(PostcodeGssCode.objects.count(), 9)

    def test_that_it_does_not_import_the_header_row(self):
        # setup
        self._import_data_from('NSPL_sample.csv')
        record = PostcodeGssCode.objects.filter(postcode_index='pcd').first()
        self.assertEqual(record, None)
