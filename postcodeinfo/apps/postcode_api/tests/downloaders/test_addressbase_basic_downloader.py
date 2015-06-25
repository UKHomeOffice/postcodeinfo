import os
from django.test import TestCase
from mock import patch

import ftplib

from postcode_api.downloaders.addressbase_basic_downloader import AddressBaseBasicDownloader


class AddressBaseBasicDownloaderTestCase(TestCase):

    def _downloader(self, mock_dl_mgr):
        return AddressBaseBasicDownloader(mock_dl_mgr)

    def _sample_data_file(self, filename):
        return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
    def test_that_it_opens_an_ftp_connection_with_the_right_parameters(self, mock):
        ftpuser = os.environ.setdefault('OS_FTP_USERNAME', 'ftpuser')
        ftppwd = os.environ.setdefault('OS_FTP_PASSWORD', 'ftppwd')

        self._downloader(mock).download()
        mock.open.assertCalledWith('osmmftp.os.uk', ftpuser, ftppwd)

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
    def test_that_it_changes_to_the_source_dir(self, mock):
        os.environ.setdefault('OS_FTP_ORDER_DIR', 'my/dir')

        self._downloader(mock).download()
        mock.ftp_client.cwd.assertCalledWith('my/dir')

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
    def test_that_it_downloads_all_if_needed_with_the_right_parameters(self, mock):
        self._downloader(mock).download('/my/local/dir', True)
        mock.download_all_if_needed.assertCalledWith('/my/local/dir', True)

        self._downloader(mock).download('/some/other/dir', False)
        mock.download_all_if_needed.assertCalledWith('/some/other/dir', False)

    @patch('postcode_api.downloaders.addressbase_basic_downloader.AddressBaseBasicDownloader.local_files', return_value=['local_files'])
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
    def test_that_when_the_ftp_call_raises_an_exception_and_local_files_exist_it_returns_the_local_files(self, mock, mock_local_files):
        dl = self._downloader(mock)
        dl.ftp_client().cwd.side_effect = ftplib.error_perm
        self.assertEqual( ['local_files'], dl.download('/some/other/dir', False) )


    @patch('postcode_api.downloaders.addressbase_basic_downloader.AddressBaseBasicDownloader.files_from_s3', return_value=['files from s3'])
    @patch('postcode_api.downloaders.addressbase_basic_downloader.AddressBaseBasicDownloader.local_files', return_value=[])
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
    def test_that_when_the_ftp_call_raises_an_exception_and_local_files_dont_exist_it_returns_the_files_from_s3(self, mock, mock_local_files, mock_s3_files):
        dl = self._downloader(mock)
        dl.ftp_client().cwd.side_effect = ftplib.error_perm
        #dl.ftp_client.cwd.side_effect=ftplib.error_perm
        self.assertEqual( ['files from s3'], dl.download('/some/other/dir', False) )

    # describe: local_files
    @patch('glob.glob', return_value=['f1','f2'])
    def test_that_it_globs_for_zipped_csv_files_in_local_dir(self, mock):
        result = self._downloader(mock).local_files('/local/dir/')
        mock.assertCalledWith('/local/dir/*csv.zip')
        self.assertEqual(['f1','f2'], result)

    # describe: files_from_s3
    @patch('postcode_api.downloaders.s3_adapter.S3Adapter')
    def test_that_it_lists_addressbase_files_in_the_s3_adapters_bucket(self, mock):
        dl = self._downloader(mock)
        dl.files_from_s3
        mock.bucket.list.assertCalledWith('AddressBase')


