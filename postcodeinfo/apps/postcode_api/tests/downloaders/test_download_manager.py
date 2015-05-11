import os

from django.test import TestCase
from mock import patch, MagicMock

from postcode_api.models import Download
from postcode_api.downloaders.download_manager import DownloadManager

def subject():
  return DownloadManager()

class DownloadManagerTestCase(TestCase):
  def __existing_record(self, headers):
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
    self.assertEqual( subject().chunk_size(), 1234 )

  @patch('os.environ.get')
  def test_that_it_defaults_chunk_size_to_4192_if_not_set(self, mock):
    mock.return_value = None
    self.assertEqual( subject().chunk_size(), 4192 )

  def test_that_given_a_url_and_a_dir_it_returns_the_last_element_appended_to_the_dir(self):
    self.assertEqual( subject().filename('/my/dir/path/', 'http://some.com/some/file.json'), '/my/dir/path/file.json' )


  # describe: existing_download_record
  def test_that_a_record_that_matches_url_etag_and_last_modified_is_returned(self):
    headers = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
    self.assertEqual( self.__existing_record(headers), subject().existing_download_record('http://my/url.html', headers) )

  def test_that_a_record_that_matches_url_etag_but_not_last_modified_is_not_returned(self):
    headers_existing = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
    headers_looked_for = {'etag': headers_existing['etag'], 'last-modified': '2015-01-01 23:23:23'}
    existing_record = self.__existing_record(headers_existing)
    self.assertEqual( None, subject().existing_download_record('http://my/url.html', headers_looked_for) )

  def test_that_a_record_that_matches_url_and_last_modified_but_not_etag_is_not_returned(self):
    headers_existing = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
    headers_looked_for = {'etag': 'foobar', 'last-modified': headers_existing['last-modified']}
    existing_record = self.__existing_record(headers_existing)
    self.assertEqual( None, subject().existing_download_record('http://my/url.html', headers_looked_for) )

  # describe: download_is_needed
  def test_that_when_given_a_thing_it_returns_false(self):
    self.assertEqual( False, subject().download_is_needed('something') )

  def test_that_when_given_nothing_it_returns_true(self):
    self.assertEqual( True, subject().download_is_needed(None) )

  # describe: record_download
  def test_that_it_creates_a_download_record_with_the_right_attributes(self):
    headers = {'etag': '12345', 'last-modified': '2015-05-09 09:12:35'}
    dl = subject().record_download('http://my/url.html', '/my/dir/path/', headers)
    self.assertEqual( 'http://my/url.html', dl.url )
    self.assertEqual( '12345', dl.etag )
    self.assertEqual( '/my/dir/path/url.html', dl.local_filepath )
    self.assertEqual( 'downloaded', dl.state )
    self.assertEqual( 'http://my/url.html', dl.url )


