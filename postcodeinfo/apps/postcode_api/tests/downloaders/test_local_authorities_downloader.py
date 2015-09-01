import mock
import unittest

from postcode_api.downloaders import LocalAuthoritiesDownloader


class LocalAuthoritiesDownloaderTest(unittest.TestCase):

    def test_url_is_the_authoritative_url(self):
        downloader = LocalAuthoritiesDownloader()
        url = downloader._authoritative_url()
        self.assertEqual(url, downloader.url)

    def test_that_the_default_url_can_be_overridden_with_an_env_var(self):
        mock_env = {'LOCAL_AUTHORITIES_DUMP_URL': 'blah'}
        with mock.patch.dict('os.environ', mock_env):
            downloader = LocalAuthoritiesDownloader()
            self.assertEqual('blah', downloader.url)
        
