import datetime
import mock
import unittest

from postcode_api.downloaders.postcode_gss_code import PostcodeGssCodeDownloader
from postcode_api.downloaders.download_manager import DownloadManager


def mock_index_json(*args, **kwargs):
    latest = kwargs.pop('latest', datetime.datetime(2015, 7, 7) )
    older = kwargs.pop('older', datetime.datetime(2015, 5, 2) )
    title = kwargs.pop('title', 'National Statistics Postcode Lookup (UK)' )

    j = {
            'records': [
                {
                    'title': title,
                    'updated': latest,
                    'links': [
                        {
                            'type': 'open',
                            'href': 'http://example.com/csv1'},
                        {
                            'type': 'details',
                            'href': 'http://example.com/nope'}]},
                {
                    'title': title,
                    'updated': older,
                    'links': [
                        {
                            'type': 'open',
                            'href': 'http://example.com/csv2'}]}]}
    return j


class PostcodeGssCodeDownloaderTest(unittest.TestCase):

    def _mock_geoportal_response(self):
        return open(
            self._sample_data_file('os_geoportal_response.json'),
            'rb').read()

    def mock_open(self):
        open_name = 'postcode_api.downloaders.http.open'
        self.mocked_file = mock.mock_open()
        return mock.patch(open_name, self.mocked_file, create=True)

    def test_downloads_latest_record(self):

        with mock.patch.object(DownloadManager, 'download') as mock_file_download, \
                mock.patch('requests.get') as http_get:

            mock_index = mock.MagicMock()
            mock_index.json.return_value = mock_index_json()

            def index_then_csv(*args, **kwargs):
                if '/rest/find/document' in args[0]:
                    return mock_index
                return mock.MagicMock()

            http_get.side_effect = index_then_csv

            downloader = PostcodeGssCodeDownloader()
            downloader.download('/tmp')

            self.assertEqual(1, mock_index.json.call_count)
            mock_file_download.assert_called_with(url='http://example.com/csv1')
