import datetime
import mock
import unittest

from postcode_api.downloaders.s3 import S3Cache
from postcode_api.downloaders.http import HttpDownloader


class S3CacheTest(unittest.TestCase):


    def test_uses_s3_file_if_exists_and_up_to_date(self):

        timestamp = 'Sun, 23 Mar 2014 13:05:10 GMT'

        def ts(dt):
            return '{0:%Y-%m-%dT%H:%M:%S.000Z}'.format(dt)

        class StubDownloader(S3Cache, HttpDownloader):
            pass

        with mock.patch('requests.head') as head, \
                mock.patch('requests.get') as get, \
                mock.patch('django.conf.settings') as settings, \
                mock.patch('boto.s3.connect_to_region') as s3_conn:

            settings.AWS = {
                'region_name': 'test_region',
                's3_bucket_name': 'test_bucket'
            }

            head.return_value.headers = {
                'last-modified': timestamp,
                'content-length': 0}

            downloader = StubDownloader('http://example.com/dummy_url')
            downloader.bucket

            s3_conn.assertCalledWith('test_region')
            s3_bucket = s3_conn.return_value.get_bucket.return_value
            s3_bucket.assertCalledWith('test_bucket')

            s3_key = s3_bucket.get_key.return_value
            in_date = datetime.datetime(2014, 3, 24, 12)
            out_of_date = datetime.datetime(2014, 3, 22, 12)
            cases = [
                (s3_key, in_date, False),
                (s3_key, out_of_date, True),
                (None, in_date, True),
                (None, out_of_date, True)]

            for key, last_modified, use_local in cases:
                s3_key.last_modified = ts(last_modified)

                downloader.download('/tmp')

                self.assertEqual(use_local, get.called)

    def test_that_an_empty_last_modified_does_not_cause_a_crash(self):
        mock_obj = mock.MagicMock('mock object', last_modified=None)
        cache = S3Cache()
        last_mod = cache._last_modified_with_timezone(mock_obj)
        self.assertEqual(last_mod, None)
