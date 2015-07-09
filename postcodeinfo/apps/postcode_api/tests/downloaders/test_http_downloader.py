# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
import mock
import os
import responses
import tempfile
import unittest
import StringIO

from dateutil import parser as dateparser

from postcode_api.downloaders.http import HttpDownloader


class HttpDownloaderTest(unittest.TestCase):

    def setUp(self):
        self.mocked_file = None

    def test_init_chunk_size_from_env(self):
        for env, size in [
                ({}, 4192),
                ({'DOWNLOAD_CHUNK_SIZE': '1234'}, 1234)]:

            with mock.patch.dict('os.environ', env):
                downloader = HttpDownloader('dummy_url')
                self.assertEqual(size, downloader.chunk_size)

    def mock_open(self):
        open_name = 'postcode_api.downloaders.http.open'
        self.mocked_file = mock.mock_open()
        return mock.patch(open_name, self.mocked_file, create=True)

    def test_download(self):
        with self.mock_open() as mock_open, \
                mock.patch('tempfile.mkdtemp') as mkdtemp, \
                mock.patch('requests.get'), \
                mock.patch('requests.head'):

            test_url = 'http://example.com/some/dummy_url'
            test_dir = 'foo'
            test_filename = test_url.split('/')[-1]

            mkdtemp.return_value = test_dir

            for url, dest_dir, path in [
                    (test_url, None, '%s/%s' % (test_dir, test_filename)),
                    (test_url, '/tmp', '/tmp/%s' % test_filename)]:
                HttpDownloader(url).download(dest_dir)
                mock_open.assert_called_with(path, 'wb')

    def test_download_file(self):
        content_length = 1000
        with mock.patch('requests.head') as head, \
                mock.patch('requests.get') as get, \
                self.mock_open() as mock_open:

            head.return_value.headers = {'content-length': content_length}
            fake_data = ['a'] * content_length
            get.return_value.iter_content.return_value = iter(fake_data)
            url = 'http://example.com/dummy_url'

            filename = HttpDownloader(url).download('/tmp')

            self.assertEqual(['/tmp/dummy_url'], filename)
            self.mocked_file().write.assert_has_calls(
                [mock.call('a')] * content_length)

    def test_last_modified(self):
        timestamp = 'Sun, 23 Mar 2014 13:05:10 GMT'
        dt = dateparser.parse(timestamp)
        with mock.patch('requests.head') as head:
            head.return_value.headers = {'last-modified': timestamp}
            downloader = HttpDownloader('http://example.com/dummy_url')
            last_modified = downloader.last_modified()
            self.assertEqual(dt, last_modified)

    # TODO: test case when file list doesn't exist remotely - how can we handle
    # that?  It should try to retrieve ... a list of files from s3 with a given
    # name pattern?  How does it know the name pattern to use? Handle this in
    # the downloaders, probably
