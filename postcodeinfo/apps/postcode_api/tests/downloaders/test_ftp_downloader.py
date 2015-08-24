# -*- encoding: utf-8 -*-
import mock
import unittest

from dateutil import parser as dateparser
import pytz

from postcode_api.downloaders.ftp import FtpDownloader


class FTPDownloaderTest(unittest.TestCase):

    def test_login(self):
        with mock.patch('ftplib.FTP') as ftp_class:
            ftp = ftp_class.return_value
            credentials = {
                'host': 'example.com',
                'user': 'ftpuser',
                'pass': 'ftppass',
                'path': 'ftppath'}
            downloader = FtpDownloader(
                credentials['host'],
                credentials['user'],
                credentials['pass'],
                path=credentials['path'])

            downloader.ftp

            ftp_class.assertCalledWith(credentials['host'])
            ftp.login.assertCalledWith(
                credentials['user'], credentials['pass'])
            ftp.cwd.assertCalledWith(credentials['path'])

    def mock_ftp_dir(self, pattern, num_files=10):

        def mock_list(p, fn):
            self.assertEqual(pattern, p)
            for i in range(num_files):
                fn('-rw-r--r--   1 ftpuser  ftp  1024 27 Apr 10:26 %s.zip' % i)

        return mock_list

    def test_list_files(self):
        num_files = 10
        pattern = '*.zip'

        with mock.patch('ftplib.FTP') as ftp_class:
            ftp = ftp_class.return_value
            ftp.dir.side_effect = self.mock_ftp_dir(pattern, num_files)

            downloader = FtpDownloader('host', 'user', 'pass')
            files = downloader._list(pattern)

            ftp.dir.assertCalledWith(pattern)
            self.assertEqual(num_files, len(files))
            for i in range(num_files):
                self.assertEqual('%s.zip' % i, files[i])

    def mock_open(self):
        open_name = 'postcode_api.downloaders.ftp.open'
        self.mocked_file = mock.mock_open()
        return mock.patch(open_name, self.mocked_file, create=True)

    def test_download(self):
        with mock.patch('ftplib.FTP') as ftp_class, \
                mock.patch('tempfile.mkdtemp') as mkdtemp, \
                self.mock_open() as mock_open:

            test_dir = 'foo'
            ftp = ftp_class.return_value
            pattern = '*.zip'
            num_files = 10
            ftp.dir.side_effect = self.mock_ftp_dir(pattern, num_files)
            mkdtemp.return_value = test_dir

            downloader = FtpDownloader('host', 'user', 'pass')
            files = downloader.download(pattern)

            filename = lambda i: '{0}/{1}.zip'.format(test_dir, i)

            mock_open.assert_has_calls(
                [mock.call(filename(i), 'wb') for i in range(num_files)],
                any_order=True)

            self.assertEqual([filename(i) for i in range(num_files)], files)

    def test_download_file(self):
        with mock.patch('ftplib.FTP') as ftp_class, \
                mock.patch('postcode_api.downloaders.ftp.log'), \
                self.mock_open() as mock_open:

            src = 'foo'
            dest = '/tmp/foo'
            content_length = 1000

            def mock_ftp_retr(cmd, fn):
                self.assertEqual('RETR %s' % src, cmd)
                for data in 'a' * content_length:
                    fn(data)

            ftp = ftp_class.return_value
            ftp.retrbinary.side_effect = mock_ftp_retr

            downloader = FtpDownloader('host', 'user', 'pass')
            downloader._headers[src] = {'content-length': content_length}
            downloader.download_file(src, dest)

            self.mocked_file().write.assert_has_calls(
                [mock.call('a')] * content_length)

    def test_last_modified(self):
        dt = pytz.UTC.localize(dateparser.parse('27 Apr 10:26'))
        with mock.patch('ftplib.FTP') as ftp_class:

            ftp = ftp_class.return_value
            ftp.dir.side_effect = self.mock_ftp_dir('*.zip', 10)

            downloader = FtpDownloader('host', 'user', 'pass')
            downloader._list('*.zip')
            last_modified = downloader.last_modified('1.zip')
            self.assertEqual(dt, last_modified)

    def test_find_dir_with_latest_file_matching(self):
        mock_files = ['dir-a/file-2014-05-06', 'dir-b/file-2015-06-07', 'dir-c/file-2015-10-29']

        with mock.patch('ftplib.FTP'):
            downloader = FtpDownloader('host', 'user', 'pass')
            downloader._list = mock.MagicMock(return_value=mock_files)
            self.assertEqual( downloader.find_dir_with_latest_file_matching('*/file-*'), 'dir-c' )
