from django.test import TestCase

from mock import patch, MagicMock

from postcode_api.utils import ZipExtractor


class ZipExtractorTestCase(TestCase):

    @patch('zipfile.is_zipfile', return_value=True)
    @patch('postcode_api.utils.ZipExtractor.unzip')
    def test_that_when_given_a_zip_file_it_unzips_it(self,
                                                     mock_unzip,
                                                     mock_zip_file):
        ZipExtractor('/my/test/file').unzip_if_needed('*')
        mock_unzip.assertCalledWith('/my/test/file')

    @patch('zipfile.is_zipfile', return_value=False)
    @patch('postcode_api.utils.ZipExtractor.unzip')
    def test_that_when_not_given_a_zip_file_it_does_not_unzip(self,
                                                              mock_unzip,
                                                              mock_zip_file):
        rtn = ZipExtractor('/my/test/file').unzip_if_needed('*')
        assert not mock_unzip.called
