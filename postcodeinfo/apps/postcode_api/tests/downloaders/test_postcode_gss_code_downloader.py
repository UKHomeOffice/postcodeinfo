import os
from django.test import TestCase
from mock import patch
from mock import MagicMock

import responses
import requests

from postcode_api.downloaders.postcode_gss_code_downloader import PostcodeGssCodeDownloader
from postcode_api.downloaders.download_manager import DownloadManager



class PostcodeGssCodeDownloaderTestCase(TestCase):
  def __downloader(self):
    return PostcodeGssCodeDownloader()

  def __sample_data_file(self, filename):
    return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

  def __mock_geoportal_response(self):
    return open( self.__sample_data_file('os_geoportal_response.json'), 'rb' ).read()

  @patch.object(DownloadManager, 'download_if_needed')
  def test_that_download_if_needed_is_called(self, mock):
    self.__downloader().__target_href = MagicMock('http://mock/url')
    self.__downloader().download()
    self.assertTrue(mock.called)
    mock.assertCalledWith('http://mock/url', '/tmp/', False)

  @patch.object(DownloadManager, 'download_if_needed')
  def test_that_a_given_target_dir_is_passed_to_the_downloader(self, mock):
    self.__downloader().download('/my/target/dir/')
    mock.assertCalledWith('http://mock/url', '/my/target/dir/', False)

  @patch.object(DownloadManager, 'download_if_needed')
  def test_that_a_given_force_value_is_passed_to_the_downloader(self, mock):
    self.__downloader().download('/tmp/', True)
    mock.assertCalledWith('http://mock/url', '/tmp/', True)



  @responses.activate
  @patch.object(DownloadManager, 'download_if_needed')
  def test_that_it_downloads_the_most_recent_file_url_from_the_os_geoportal(self, mock):
    responses.add(responses.GET, 'https://geoportal.statistics.gov.uk/geoportal/rest/find/document?searchText=NSPL&f=pjson',
                  status=200, content_type='application/json',
                  body=self.__mock_geoportal_response(),
                  match_querystring=True)
    self.__downloader().download()
    mock.assertCalledWith('https://geoportal.statistics.gov.uk/Docs/PostCodes/NSPL_AUG_2014_csv.zip', '/tmp/', True)