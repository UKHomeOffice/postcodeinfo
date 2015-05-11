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

