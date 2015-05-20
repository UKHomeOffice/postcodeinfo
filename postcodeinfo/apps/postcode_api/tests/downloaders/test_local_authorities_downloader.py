from django.test import TestCase
from mock import patch

from postcode_api.downloaders.local_authorities_downloader import LocalAuthoritiesDownloader
from postcode_api.downloaders.download_manager import DownloadManager


class LocalAuthoritiesDownloaderTestCase(TestCase):

    def __downloader(self):
        return LocalAuthoritiesDownloader()

    @patch.object(DownloadManager, 'download_if_needed')
    def test_that_download_if_needed_is_called(self, mock):
        self.__downloader().download()
        self.assertTrue(mock.called)
        mock.assertCalledWith(
            'http://opendatacommunities.org/data/dev-local-authorities/dump', '/tmp/', False)

    @patch.object(DownloadManager, 'download_if_needed')
    def test_that_a_given_target_dir_is_passed_to_the_downloader(self, mock):
        self.__downloader().download('/my/target/dir/')
        mock.assertCalledWith(
            'http://opendatacommunities.org/data/dev-local-authorities/dump', '/my/target/dir/', False)

    @patch.object(DownloadManager, 'download_if_needed')
    def test_that_a_given_force_value_is_passed_to_the_downloader(self, mock):
        self.__downloader().download('/tmp/', True)
        mock.assertCalledWith(
            'http://opendatacommunities.org/data/dev-local-authorities/dump', '/tmp/', True)
