import os
import requests
import responses
import tempfile

from django.test import TestCase
from mock import patch, MagicMock

from postcode_api.models import Download
from postcode_api.downloaders.download_manager import DownloadManager


def subject():
    return DownloadManager()


class DownloadManagerTestCase(TestCase):

    def _existing_record(self, headers):
        existing_record = Download(url='http://my/url.html',
                                   etag=headers['etag'],
                                   last_modified=headers['last-modified'],
                                   state='downloaded',
                                   last_state_change='2015-04-03 02:01:00')
        existing_record.save()
        return existing_record

    # describe: chunk_size
    def test_that_it_takes_the_chunk_size_from_an_environment_variable_if_set(self):
        os.environ.setdefault('DOWNLOAD_CHUNK_SIZE', '1234')
        self.assertEqual(subject().chunk_size(), 1234)

    @patch('os.environ.get')
    def test_that_it_defaults_chunk_size_to_4192_if_not_set(self, mock):
        mock.return_value = None
        self.assertEqual(subject().chunk_size(), 4192)

    def test_that_given_a_url_and_a_dir_it_returns_the_last_element_appended_to_the_dir(self):
        self.assertEqual(subject().filename(
            '/my/dir/path/', 'http://some.com/some/file.json'), '/my/dir/path/file.json')

    # describe: existing_download_record
    def test_that_a_record_that_matches_url_etag_and_last_modified_is_returned(self):
        headers = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
        self.assertEqual(self._existing_record(
            headers), subject().existing_download_record('http://my/url.html', headers))

    def test_that_a_record_that_matches_url_etag_but_not_last_modified_is_not_returned(self):
        headers_existing = {
            'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
        headers_looked_for = {
            'etag': headers_existing['etag'], 'last-modified': '2015-01-01 23:23:23'}
        existing_record = self._existing_record(headers_existing)
        self.assertEqual(None, subject().existing_download_record(
            'http://my/url.html', headers_looked_for))

    def test_that_a_record_that_matches_url_and_last_modified_but_not_etag_is_not_returned(self):
        headers_existing = {
            'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
        headers_looked_for = {
            'etag': 'foobar', 'last-modified': headers_existing['last-modified']}
        existing_record = self._existing_record(headers_existing)
        self.assertEqual(None, subject().existing_download_record(
            'http://my/url.html', headers_looked_for))

    # describe: download_is_needed
    def test_that_when_given_a_thing_it_returns_false(self):
        self.assertEqual(False, subject().download_is_needed('something'))

    def test_that_when_given_nothing_it_returns_true(self):
        self.assertEqual(True, subject().download_is_needed(None))

    # describe: record_download
    def test_that_it_creates_a_download_record_with_the_right_attributes(self):
        headers = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
        dl = subject().record_download(
            'http://my/url.html', '/my/dir/path/', headers)
        self.assertEqual('http://my/url.html', dl.url)
        self.assertEqual('12345', dl.etag)
        self.assertEqual('/my/dir/path/url.html', dl.local_filepath)
        self.assertEqual('downloaded', dl.state)
        self.assertEqual('http://my/url.html', dl.url)

    # describe: get_headers
    @patch('requests.head')
    def test_that_it_makes_a_head_request_to_the_given_url_and_follows_redirects(self, mock):
        returned = subject().get_headers('http://some.url/')
        mock.assertCalledWith('http://some.url/', allow_redirects=True)

    @responses.activate
    def test_that_it_returns_the_headers(self):
        headers = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
        responses.add(responses.HEAD, 'http://some.url/', body=None,
                      status=200, adding_headers=headers)
        returned_headers = subject().get_headers('http://some.url/')
        self.assertEqual(headers['etag'], returned_headers['etag'])
        self.assertEqual(
            headers['last-modified'], returned_headers['last-modified'])

    # describe: download_to_file
    @responses.activate
    def test_that_it_downloads_the_give_url_to_the_given_file_path(self):
        responses.add(responses.GET, 'http://some.url/test.file', body='file contents',
                      status=200)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, 'test123.txt')
        subject().download_to_file('http://some.url/test.file', temp_file_path)
        temp_file = open(temp_file_path)
        contents = temp_file.read()
        self.assertEqual('file contents', contents)
        os.remove(temp_file_path)

    # describe: download_to_dir
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_to_file')
    def test_that_it_calls_download_to_file_with_the_right_arguments(self, mock):
        subject().download_to_dir(
            'http://some.url/test.file', '/my/dir/path/', {'content-length': '1234'})
        mock.assertCalledWith(
            'http://some.url/test.file', '/my/dir/path/test.file', 4192, 1234)

    # describe: download_if_needed
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_headers')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_is_needed')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.do_download')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.existing_download_record')
    def test_that_when_download_is_needed_then_it_downloads_the_given_url_to_the_given_dir(self, mock_hdrs, mock_dl_needed, mock_do_download, mock_existing_download_record):
        mock_dl_needed.return_value = True
        rtn_val = subject().download_if_needed(
            'http://some.url/test.file', '/my/dir/path/')
        mock_do_download.assertCalledWith(
            'http://some.url/test.file', '/my/dir/path/')

    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_headers')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_is_needed')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.do_download')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.existing_download_record')
    def test_that_when_download_is_not_needed_then_it_does_not_download(self, mock_hdrs, mock_dl_needed, mock_do_download, mock_existing_download_record):
        mock_dl_needed.return_value = False
        rtn_val = subject().download_if_needed(
            'http://some.url/test.file', '/my/dir/path/')
        self.assertEqual(rtn_val, None)

    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_headers')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_is_needed')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.do_download')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.existing_download_record')
    def test_that_when_download_is_not_needed_but_force_is_passed_then_it_does_download(self, mock_hdrs, mock_dl_needed, mock_do_download, mock_existing_download_record):
        mock_dl_needed.return_value = False
        rtn_val = subject().download_if_needed(
            'http://some.url/test.file', '/my/dir/path/', True)
        mock_do_download.assertCalledWith(
            'http://some.url/test.file', '/my/dir/path/')
