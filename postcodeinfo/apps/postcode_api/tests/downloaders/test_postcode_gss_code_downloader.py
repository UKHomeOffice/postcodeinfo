import datetime
import mock
import unittest

from postcode_api.downloaders.postcode_gss_code import PostcodeGssCodeDownloader


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

        with mock.patch.object(PostcodeGssCodeDownloader, 'download_file'), \
                mock.patch('requests.get') as http_get:

            latest = datetime.datetime(2015, 7, 7)
            older = datetime.datetime(2015, 5, 2)

            mock_index = mock.MagicMock()
            title = 'National Statistics Postcode Lookup (UK)'
            mock_index.json.return_value = {
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

            def index_then_csv(*args, **kwargs):
                if '/rest/find/document' in args[0]:
                    return mock_index
                return mock.MagicMock()

            http_get.side_effect = index_then_csv

            downloader = PostcodeGssCodeDownloader()
            downloader.download('/tmp')

            self.assertEqual(1, mock_index.json.call_count)
