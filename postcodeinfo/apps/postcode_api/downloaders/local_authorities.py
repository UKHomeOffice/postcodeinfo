# -*- encoding: utf-8 -*-
"""
Local Authorities downloader class
"""

import errno
import logging
import os

from postcode_api.caches.s3_cache import S3Cache
from postcode_api.caches.filesystem_cache import FilesystemCache
from postcode_api.caches.multi_level_caching_strategy import MultiLevelCachingStrategy
from postcode_api.downloaders.download_manager import DownloadManager

from .http import HttpDownloader
#from .s3 import S3Cache

log = logging.getLogger(__name__)


class LocalAuthoritiesDownloader():

    def _authoritative_url(self):
        default_url = 'http://opendatacommunities.org/downloads/graph?uri='\
                      'http://opendatacommunities.org/graph/dev-'\
                      'local-authorities'

        return os.environ.get('LOCAL_AUTHORITIES_DUMP_URL') or default_url

    def __init__(self, *args, **kwargs):
        self.dest_dir = kwargs.pop('destination_dir', '/tmp/local_authorities')

        self.cache_key = 'dev-local-authorities'
        self.http_dl = HttpDownloader(self._authoritative_url())

    def download(self, dest_dir):
        dl_mgr = DownloadManager(
            destination_dir=dest_dir, downloader=self.http_dl, caching_strategy=self._caching_strategy())
        return dl_mgr.download(url=self._authoritative_url())

    def _local_filepath(self):
        filename = self.http_dl.attachment_filename()
        return os.path.join(self.dest_dir, filename)

    def _caching_strategy(self):
        caches = [
            FilesystemCache(dir='/tmp/local_authorities'),
            S3Cache()
        ]
        return MultiLevelCachingStrategy(caches=caches)
