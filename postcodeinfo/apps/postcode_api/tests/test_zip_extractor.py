from django.test import TestCase

from mock import patch

from postcode_api.utils import ZipExtractor


class ZipExtractorTestCase(TestCase):

    def setUp(self):
        self.patch_unzip = patch('postcode_api.utils.ZipExtractor.unzip')
        self.mock_unzip = self.patch_unzip.start()

    def tearDown(self):
        self.patch_unzip.stop()

    def test_that_when_given_a_zip_file_it_unzips_it(self):
        with patch('zipfile.is_zipfile', return_value=True):
            ZipExtractor('/my/test/file').unzip_if_needed('*')
            self.mock_unzip.assertCalledWith('/my/test/file')

    def test_that_when_not_given_a_zip_file_it_does_not_unzip(self):
        with patch('zipfile.is_zipfile', return_value=False):
            ZipExtractor('/my/test/file').unzip_if_needed('*')
            assert not self.mock_unzip.called
