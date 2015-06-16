import os
from django.test import TestCase
from mock import patch
from mock import MagicMock

import responses
import requests

from postcode_api.downloaders.postcode_gss_code_downloader\
    import PostcodeGssCodeDownloader
from postcode_api.downloaders.download_manager\
    import DownloadManager


class PostcodeGssCodeDownloaderTestCase(TestCase):

    def _downloader(self):
        return PostcodeGssCodeDownloader()

    def _downloader_with_mocked_index_json(self):
        dl = self._downloader()
        dl._get_index_json = MagicMock(return_value=self._mock_geoportal_response())
        return dl

    def _sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__),
                            '../',
                            'sample_data/',
                            filename)

    def _mock_geoportal_response(self):
        return open(self._sample_data_file('os_geoportal_response.json'),
                    'rb').read()

    @patch.object(DownloadManager, 'retrieve')
    def test_that_retrieve_is_called(self, mock):
        self._downloader_with_mocked_index_json().download()
        self.assertTrue(mock.called)
        mock.assertCalledWith('http://mock/url', '/tmp/', False)

    @patch.object(DownloadManager, 'retrieve')
    def test_that_a_given_target_dir_is_passed_to_the_downloader(self, mock):
        self._downloader_with_mocked_index_json().download('/my/target/dir/')
        mock.assertCalledWith('http://mock/url', '/my/target/dir/', False)

    @patch.object(DownloadManager, 'retrieve')
    def test_that_a_given_force_value_is_passed_to_the_downloader(self, mock):
        self._downloader_with_mocked_index_json().download('/tmp/', True)
        mock.assertCalledWith('http://mock/url', '/tmp/', True)

    @responses.activate
    @patch.object(DownloadManager, 'retrieve')
    def test_that_it_downloads_the_most_recent_file_url_from_the_os_geoportal(self, mock):
        self._downloader_with_mocked_index_json().download()
        mock.assertCalledWith(
            'https://geoportal.statistics.gov.uk/Docs/PostCodes/NSPL_AUG_2014_csv.zip', '/tmp/', True)
