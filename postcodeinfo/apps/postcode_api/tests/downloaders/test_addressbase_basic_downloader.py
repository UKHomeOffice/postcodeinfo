import os
from django.test import TestCase
from mock import patch, MagicMock

import responses
import requests
import ftplib
from ftplib import FTP

from postcode_api.downloaders.addressbase_basic_downloader import AddressBaseBasicDownloader
from postcode_api.downloaders.download_manager import DownloadManager
from postcode_api.downloaders.ftp_download_manager import FTPDownloadManager


class AddressBaseBasicDownloaderTestCase(TestCase):
  def __downloader(self, mock_dl_mgr):
    return AddressBaseBasicDownloader(mock_dl_mgr)

  def __sample_data_file(self, filename):
    return os.path.join(os.path.dirname(__file__), '../', 'sample_data/', filename)

  @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
  def test_that_it_opens_an_ftp_connection_with_the_right_parameters(self, mock):
    ftpuser = os.environ.setdefault('OS_FTP_USERNAME', 'ftpuser')
    ftppwd = os.environ.setdefault('OS_FTP_PASSWORD', 'ftppwd')
    
    self.__downloader(mock).download()
    mock.open.assertCalledWith('osmmftp.os.uk', ftpuser, ftppwd)


  @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
  def test_that_it_changes_to_the_source_dir(self, mock):
    target_dir = os.environ.setdefault('OS_FTP_ORDER_DIR', 'my/dir')
    
    self.__downloader(mock).download()
    mock.ftp_client.cwd.assertCalledWith('my/dir')


  @patch('postcode_api.downloaders.ftp_download_manager.FTPDownloadManager')
  def test_that_it_downloads_all_if_needed_with_the_right_parameters(self, mock):
    self.__downloader(mock).download('/my/local/dir', True)
    mock.download_all_if_needed.assertCalledWith('/my/local/dir', True)

    self.__downloader(mock).download('/some/other/dir', False)
    mock.download_all_if_needed.assertCalledWith('/some/other/dir', False)