# -*- encoding: utf-8 -*-
import datetime
import mock
import unittest

from ...downloaders.local_authorities import LocalAuthoritiesDownloader
from ...downloaders.download_manager import DownloadManager


def mock_index_json(*args, **kwargs):
    latest_date = kwargs.pop('latest_date', datetime.datetime(2015, 7, 7))
    oldest_date = kwargs.pop('oldest_date', datetime.datetime(2013, 5, 2))
    oldest_title = kwargs.pop(
        'oldest_title', 'Local authority districts (UK) 2011 Names and Codes')
    latest_title = kwargs.pop(
        'latest_title', 'Local authority districts (UK) 2014 Names and Codes')
    oldest_filename = 'Local_authority_districts_(UK)_2011_Names_and_Codes.zip'
    latest_filename = 'Local_authority_districts_(UK)_2014_Names_and_Codes.zip'

    # NOTE - the title & date deliberately mismatch, as that's a situation
    # we've encountered with the real data.
    return {
        'records': [
            {
                'title': oldest_title,
                'updated': latest_date,
                'links': [
                    {
                        'type': 'open',
                        'href': latest_filename},
                    {
                        'type': 'details',
                        'href': 'http://example.com/nope'}]},
            {
                'title': latest_title,
                'updated': oldest_date,
                'links': [
                    {
                        'type': 'open',
                        'href': oldest_filename}]}]}


class LocalAuthoritiesDownloaderTest(unittest.TestCase):

    def test_downloads_record_with_latest_year_in_title(self):
        with mock.patch.object(DownloadManager, 'download') \
                as mock_file_download, mock.patch('requests.get') \
                as http_get:

            mock_index = mock.MagicMock()
            mock_index.json.return_value = mock_index_json()

            def index_then_csv(*args, **kwargs):
                if '/rest/find/document' in args[0]:
                    return mock_index
                return mock.MagicMock()

            http_get.side_effect = index_then_csv

            downloader = LocalAuthoritiesDownloader()
            downloader.download('/tmp')

            self.assertEqual(1, mock_index.json.call_count)
            mock_file_download.assert_called_with(
                url='Local_authority_districts_(UK)_2011_Names_and_Codes.zip')
