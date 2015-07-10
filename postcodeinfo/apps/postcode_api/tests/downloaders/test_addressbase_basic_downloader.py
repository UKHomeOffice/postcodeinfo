# -*- encoding: utf-8 -*-
import mock
import unittest

from postcode_api.downloaders import AddressBaseBasicDownloader


class AddressBaseBasicDownloaderTest(unittest.TestCase):

    def mock_env(self, env=None):
        if env is None:
            ftpuser = 'ftpuser'
            ftppass = 'ftppass'
            ftpdir = 'my/dir'
            self.env = {
                'OS_FTP_USERNAME': ftpuser,
                'OS_FTP_PASSWORD': ftppass,
                'OS_FTP_ORDER_DIR': ftpdir}
        else:
            self.env = env

        return mock.patch.dict('os.environ', self.env, clear=True)

    def test_passes_ftp_credentials(self):
        with mock.patch('ftplib.FTP') as ftp_class, self.mock_env():
            ftp = ftp_class.return_value
            AddressBaseBasicDownloader().download()
            ftp_class.assertCalledWith('osmmftp.os.uk')
            ftp.login.assertCalledWith(
                self.env['OS_FTP_USERNAME'], self.env['OS_FTP_PASSWORD'])
            ftp.cwd.assertCalledWith(self.env['OS_FTP_ORDER_DIR'])

    def test_complains_if_ftp_credentials_not_set(self):
        logger = 'postcode_api.downloaders.addressbase_basic.log'
        with mock.patch('ftplib.FTP'), \
                mock.patch(logger) as log, \
                self.mock_env({}):

            AddressBaseBasicDownloader().download()

            log.error.assert_has_calls([
                mock.call('OS_FTP_USERNAME not set!'),
                mock.call('OS_FTP_PASSWORD not set!')])

    def test_downloads_files_matching_pattern(self):
        with mock.patch('ftplib.FTP') as ftp_class, self.mock_env():
            ftp = ftp_class.return_value
            AddressBaseBasicDownloader().download()
            self.assertTrue(ftp.dir.called)
            self.assertEqual('*_csv.zip', ftp.dir.call_args[0][0])
