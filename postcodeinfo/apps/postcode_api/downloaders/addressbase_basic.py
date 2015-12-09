# -*- encoding: utf-8 -*-
"""
AddressBase Basic downloader class
"""

import logging
import os

from .ftp import FtpDownloader
from postcode_api.caches.s3_cache import S3Cache
from .download_manager import DownloadManager
from postcode_api.caches.filesystem_cache import FilesystemCache
from postcode_api.caches.multi_level_caching_strategy import MultiLevelCachingStrategy

log = logging.getLogger(__name__)


class AddressBaseBasicDownloader(object):

    def __init__(self, *args, **kwargs):
        self.ftp_host = kwargs.pop('ftp_host', 'osmmftp.os.uk')
        self.ftp_username = kwargs.pop(
            'ftp_username', os.environ.get('OS_FTP_USERNAME'))
        self.ftp_password = kwargs.pop(
            'ftp_password', os.environ.get('OS_FTP_PASSWORD'))
        self._check_ftp_params_present()
        self.caches = kwargs.pop('caches', self._default_caches())
        self.caching_strategy = kwargs.pop('caching_strategy', self._default_caching_strategy())

    def _default_caches(self):
        return [
            FilesystemCache(dir='/tmp/addressbase_basic'),
            S3Cache()
        ]

    def _default_caching_strategy(self):
        return MultiLevelCachingStrategy(caches=self.caches)

    def _check_ftp_params_present(self):
        if not self.ftp_username:
            log.error('OS_FTP_USERNAME not set!')
        if not self.ftp_password:
            log.error('OS_FTP_PASSWORD not set!')


    def download(self, dest_dir):
        """
        Fetch the URL of the latest NSPL CSV and download it.
        """

        log.info('looking for dir with latest files')
        latest_dir = self.find_dir_with_latest_full_file()
        log.info('latest_dir = {latest_dir}'.format(latest_dir=latest_dir))

        ftp_downloader = FtpDownloader(self.ftp_host,
                                       self.ftp_username,
                                       self.ftp_password,
                                       latest_dir)

        dl_mgr = DownloadManager(
            destination_dir=dest_dir, downloader=ftp_downloader,
            caching_strategy=self.caching_strategy)

        return dl_mgr.download_all_matching(pattern='*_csv.zip')

    # Ordnance Survey's update mechanism creates a *new* order number
    # for every update, so we cannot predict ahead of time what the
    # directory path will be.
    # So we work it out as follows:
    # - the files are all called AddressBase_FULL_YYYY-MM-DD_NNN_csv.zip
    # - get ALL the files matching that pattern in all the subdirectories
    # - split into path / filename
    # - sort by filename
    # - the last file should be the latest, so use the directory containing it
    def find_dir_with_latest_full_file(self):
        # have to create new object rather than exploiting the
        # inheritance heirarchy, as this method is called during
        # initialisation
        root_path = '../from-os/'
        tmp_ftp = FtpDownloader('osmmftp.os.uk',
                                os.environ.get('OS_FTP_USERNAME'),
                                os.environ.get('OS_FTP_PASSWORD'),
                                root_path)

        latest_dir = tmp_ftp.find_dir_with_latest_file_matching(
            '*/AddressBase_FULL_*')
        if latest_dir:
            return root_path + latest_dir
