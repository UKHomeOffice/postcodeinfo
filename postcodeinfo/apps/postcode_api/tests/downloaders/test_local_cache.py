import datetime
import mock
import time
import unittest

from postcode_api.downloaders.filesystem import LocalCache
from postcode_api.downloaders.http import HttpDownloader


class LocalCacheTest(unittest.TestCase):

    def test_uses_local_file_if_exists_and_up_to_date(self):

        timestamp = 'Sun, 23 Mar 2014 13:05:10 GMT'

        def ts(dt):
            return time.mktime(dt.timetuple())

        in_date = datetime.datetime(2014, 3, 24, 12)
        out_of_date = datetime.datetime(2014, 3, 22, 12)
        cases = [
            (True, in_date, False),
            (True, out_of_date, True),
            (False, in_date, True),
            (False, out_of_date, True)]

        class StubDownloader(LocalCache, HttpDownloader):
            pass

        pkg = lambda x: '%s.%s' % ('postcode_api.downloaders.filesystem', x)
        with mock.patch(pkg('exists')) as exists, \
                mock.patch(pkg('getmtime')) as getmtime, \
                mock.patch(pkg('mktime')) as mktime, \
                mock.patch('requests.get') as get, \
                mock.patch('requests.head') as head:

            head.return_value.headers = {
                'last-modified': timestamp,
                'content-length': 0}

            for exists_, mtime, use_local in cases:
                getmtime.return_value = ts(mtime)
                mktime.return_value = time.mktime(mtime.timetuple())
                exists.return_value = exists_

                downloader = StubDownloader('http://example.com/dummy_url')
                downloader.download('/tmp')

                self.assertEqual(use_local, get.called)

    def test_stat_float_times_false(self):
        with mock.patch('os.stat_float_times') as sft:
            sft.return_value = False

            self.test_uses_local_file_if_exists_and_up_to_date()
