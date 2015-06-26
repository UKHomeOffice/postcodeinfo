import os
import pytz
import responses
import tempfile

from django.test import TestCase
from mock import patch, MagicMock
from dateutil import parser
from datetime import datetime, timedelta

from postcode_api.models import Download
from postcode_api.downloaders.download_manager import DownloadManager


def subject():
    return DownloadManager()


class DownloadManagerTestCase(TestCase):

    def _format_datetime(self, header):
        return pytz.UTC.localize(parser.parse(header))

    def _existing_record(self, headers):
        existing_record = Download(url='http://my/url.html',
                                   etag=headers['etag'],
                                   last_modified=self._format_datetime(
                                       headers['last-modified']),
                                   state='downloaded',
                                   last_state_change='2015-04-03T02:01:00+00:00')
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

    # describe: get_headers
    @patch('requests.head')
    def test_that_it_makes_a_head_request_to_the_given_url_and_follows_redirects(self, mock):
        subject().get_headers('http://some.url/')
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

    # describe: retrieve
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_last_modified', return_value='12345')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_from_s3')
    def test_that_when_the_local_copy_is_not_up_to_date_then_it_gets_from_s3(self, mock_get_from_s3, mock_last_modified):
        s = subject()
        s._local_copy_up_to_date = MagicMock(False)
        s.retrieve('test.url', '/local/path')
        mock_get_from_s3.assertCalledWith('/local/path', '12345')

    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_last_modified', return_value='12345')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_from_s3')
    def test_that_when_the_local_copy_is_up_to_date_then_it_does_not_get_from_s3(self, mock_get_from_s3, mock_last_modified):
        s = subject()
        s.local_copy_up_to_date = MagicMock(True)
        s.retrieve('test.url', '/local/path')
        assert not mock_get_from_s3.called

    @patch('postcode_api.downloaders.download_manager.DownloadManager.filename', return_value='/my/local/filename')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_last_modified', return_value='12345')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_from_s3')
    def test_that_it_returns_the_local_file_path(self, mock_get_from_s3, mock_last_modified, mock_filename):
        s = subject()
        s.local_copy_up_to_date = MagicMock(True)
        self.assertEqual( '/my/local/filename', s.retrieve('test.url', '/local/path') )
        

    # describe: get_from_s3
    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_adapter')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_last_modified', return_value='12345')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_object_is_up_to_date', return_value=True)
    def test_that_when_the_s3_object_is_up_to_date_it_downloads_the_file_from_s3(self, mock_s3_object_is_up_to_date, mock_get_last_modified, mock_s3_adapter):
        s = subject()
        s.get_from_s3('test.url', '/local/path', '12345')
        self.assertEqual(True, mock_s3_adapter().download.called )

    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_adapter')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_object_is_up_to_date', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_to_file', return_value=True)
    def test_that_when_the_s3_object_is_not_up_to_date_it_downloads_the_file_locally(self, mock_download_to_file, mock_s3_object_is_up_to_date, mock_s3_adapter):
        s = subject()
        s.get_from_s3('test.url', '/local/path', '12345')
        mock_download_to_file.assertCalledWith('test.url', '/local/path')

    
    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_adapter')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_last_modified', return_value='12345')
    @patch('postcode_api.downloaders.download_manager.DownloadManager.s3_object_is_up_to_date', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.download_to_file', return_value=True)
    def test_that_when_the_s3_object_is_not_up_to_date_it_uploads_the_local_file_to_s3(self, mock_download_to_file, mock_s3_object_is_up_to_date, mock_get_last_modified, mock_s3_adapter):
        s = subject()
        s.get_from_s3('test.url', '/local/path', '12345')
        mock_s3_adapter.upload.assertCalledWith('test.url', '/local/path')

    # describe: local_copy_up_to_date
    @patch('postcode_api.downloaders.download_manager.DownloadManager._in_local_storage', return_value=True)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=True)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_file_is_in_local_storage_and_up_to_date_it_returns_true(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date, mock_in_local_storage):
        self.assertEqual( True, subject().local_copy_up_to_date('local/path', 'remote timestamp') )

    @patch('postcode_api.downloaders.download_manager.DownloadManager._in_local_storage', return_value=True)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_file_is_in_local_storage_and_not_up_to_date_it_returns_false(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date, mock_in_local_storage):
        self.assertEqual( False, subject().local_copy_up_to_date('local/path', 'remote timestamp') )

    @patch('postcode_api.downloaders.download_manager.DownloadManager._in_local_storage', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=True)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_file_is_not_in_local_storage_it_returns_false(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date, mock_in_local_storage):
        self.assertEqual( False, subject().local_copy_up_to_date('local/path', 'remote timestamp') )

    # describe: s3_object_is_up_to_date
    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=True)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_s3_object_exists_and_is_up_to_date_it_returns_true(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date):
        s3_object = MagicMock(last_modified='12345')
        self.assertEqual( True, subject().s3_object_is_up_to_date(s3_object, 'remote timestamp') )
    
    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_s3_object_exists_and_is_not_up_to_date_it_returns_false(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date):
        s3_object = MagicMock(last_modified='12345')
        self.assertEqual( False, subject().s3_object_is_up_to_date(s3_object, 'remote timestamp') )

    @patch('postcode_api.downloaders.download_manager.DownloadManager.up_to_date', return_value=False)
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='12345')
    @patch('os.path.getmtime', return_value='12345')
    def test_that_when_the_s3_object_does_not_exist_it_returns_true(self, mock_file_timestamp, mock_format_time_for_orm, mock_up_to_date):
        self.assertEqual( False, subject().s3_object_is_up_to_date(None, 'remote timestamp') )
    
    # describe test_up_to_date
    def test_that_when_copy_timestamp_is_greater_than_source_timestamp_it_returns_true(self):
        self.assertEqual( True, subject().up_to_date( datetime.now(), datetime.now() - timedelta(hours=1) ) )

    def test_that_when_copy_timestamp_is_equal_to_source_timestamp_it_returns_true(self):
        now = datetime.now()
        self.assertEqual( True, subject().up_to_date( now, now ) )

    def test_that_when_copy_timestamp_is_less_than_source_timestamp_it_returns_false(self):
        self.assertEqual( False, subject().up_to_date( datetime.now() - timedelta(hours=1), datetime.now() ) )

    # describe: get_last_modified
    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_headers', return_value={'last-modified':'some time ago'})
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='formatted time')
    def test_that_it_gets_headers_with_the_given_url(self, mock_format_time_for_orm, mock_get_headers):
        result = subject().get_last_modified('a.url')
        mock_get_headers.assertCalledWith('a.url')
        mock_format_time_for_orm.assertCalledWith('some time ago')
        self.assertEqual('formatted time', result)

    @patch('postcode_api.downloaders.download_manager.DownloadManager.get_headers', return_value=[{'last-modified':'some time ago'},{'last-modified':'some other time'}])
    @patch('postcode_api.downloaders.download_manager.DownloadManager.format_time_for_orm', return_value='formatted time')
    def test_that_when_headers_is_a_list_it_uses_the_first_element(self, mock_format_time_for_orm, mock_get_headers):
        subject().get_last_modified('a.url')
        mock_format_time_for_orm.assertCalledWith('some time ago')
        
    # describe format_time_for_orm
    def test_that_given_a_string_it_returns_a_datetime(self):
        result = subject().format_time_for_orm('17-12-2015 00:01:02')
        self.assertEqual( True, isinstance(result, datetime) )


    # TODO: test case when file list doesn't exist remotely - how can we handle that?
    # It should try to retrieve ... a list of files from s3 with a given name pattern?
    # How does it know the name pattern to use? Handle this in the downloaders, probably
