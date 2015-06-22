import os
import requests
import responses
import tempfile
import ftplib
import __builtin__

from django.test import TestCase
from mock import call, patch, MagicMock, ANY

from postcode_api.models import Download
from postcode_api.downloaders.ftp_download_manager import FTPDownloadManager


def subject():
    return FTPDownloadManager()


class FTPDownloadManagerTestCase(TestCase):

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.ftp_login')
    def test_that_open_logs_into_the_given_host_with_the_given_username_and_password(self, mock_ftp_login):
        rtn = subject().open('my.ftp.host', 'my_username', 'my_password')
        mock_ftp_login.assertCalledWith(
            'my.ftp.host', 'my_username', 'my_password')

    @patch('ftplib.FTP')
    def test_that_ftp_login_logs_into_the_given_host_with_the_given_username_and_password(self, mock_ftp):
        rtn = subject().ftp_login('my.ftp.host', 'my_username', 'my_password')
        mock_ftp.assertCalledWith('my.ftp.host')
        mock_ftp.login.assertCalledWith('my_username', 'my_password')

    # describe: list_files
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.get_headers')
    def test_that_it_passes_the_given_pattern_to_get_headers(self, mock):
        mock.return_value = [{'url': '/my/url/1'}, {'url': '/my/url/2'}]
        subject().list_files('my pattern')
        mock.assertCalledWith('my pattern')

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.get_headers')
    def test_that_it_returns_an_array_of_the_urls(self, mock):
        mock.return_value = [{'url': '/my/url/1'}, {'url': '/my/url/2'}]
        self.assertEqual(
            ['/my/url/1', '/my/url/2'], subject().list_files('my pattern'))

    # describe: download_all_if_needed
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.retrieve')
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.list_files')
    def test_that_it_calls_retrieve_for_each_listed_file(self, mock_list_files, mock_dl_if_needed):
        mock_list_files.return_value = ['file/1', 'file/2']
        mock_dl_if_needed.side_effect = ['/local/file/1', '/local/file/2']
        calls = [call('file/1', '/dir/path', False),
                 call('file/2', '/dir/path', False)]
        subject().download_all_if_needed('my pattern', '/dir/path')
        mock_dl_if_needed.assert_has_calls(calls)

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.retrieve')
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.list_files')
    def test_that_it_returns_the_local_filepath_of_all_downloads_performed(self, mock_list_files, mock_dl_if_needed):
        mock_list_files.return_value = ['file/1', 'file/2']
        mock_dl_if_needed.side_effect = ['/local/file/1', '/local/file/2']
        self.assertEqual(["/local/file/1", "/local/file/2"],
                         subject().download_all_if_needed('my pattern', '/dir/path'))

    # describe get_headers
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.files_in_dir', return_value=[])
    def test_that_it_gets_files_in_the_current_directory_matching_the_given_pattern(self, mock):
        subject().get_headers('my pattern')
        mock.assertCalledWith('my pattern')

    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.interpret_ls_line')
    @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager.files_in_dir')
    def test_that_it_returns_the_files_mapped_with_interpret_ls_line(self, mock_files_in_dir, mock_interpret_ls_line):
        mock_files_in_dir.return_value = ["line 1", "line 2"]
        mock_interpret_ls_line.side_effect = [
            'interpreted line 1', 'interpreted line 2']
        self.assertEqual(
            ['interpreted line 1', 'interpreted line 2'], subject().get_headers('my pattern'))

    # describe interpret_ls_line
    def test_that_it_parses_the_line_into_the_correct_dict(self):
        line = '-rw-r--r--   1 alistairdavidson  staff  1271 27 Apr 10:26 Dockerfile'
        interpreted_line = subject().interpret_ls_line(line)
        self.assertEqual('-rw-r--r--', interpreted_line['permissions'])
        self.assertEqual(1271, interpreted_line['content-length'])
        self.assertEqual('27 Apr 10:26', interpreted_line['last-modified'])
        self.assertEqual('Dockerfile', interpreted_line['url'])
        self.assertEqual(None, interpreted_line['etag'])

    # describe download_to_dir
    @patch.object(__builtin__, 'open')
    def test_that_it_opens_a_file_with_the_right_name_in_the_right_dir(self, mock_open):
        s = subject()
        s.ftp_client = MagicMock()
        s.download_to_dir('/my/remote/file.path', '/local/file/path', {})
        mock_open.assertCalledWith('/local/file/path')

    @patch.object(__builtin__, 'open')
    def test_that_it_retrieves_the_right_file(self, mock_open):
        s = subject()
        s.ftp_client = MagicMock()
        s.download_to_dir('/my/remote/file.path', '/local/file/path', {})
        s.ftp_client.retrbinary.assertCalledWith(
            "RETR /my/remote/file.path", ANY)
