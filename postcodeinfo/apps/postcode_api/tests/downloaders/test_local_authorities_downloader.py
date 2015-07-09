import mock
import unittest

from postcode_api.downloaders import LocalAuthoritiesDownloader


class LocalAuthoritiesDownloaderTest(unittest.TestCase):

    def test_url(self):
        downloader = LocalAuthoritiesDownloader()
        url = 'http://opendatacommunities.org/data/dev-local-authorities/dump'
        self.assertEqual(url, downloader.url)
