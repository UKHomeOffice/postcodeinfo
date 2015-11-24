# -*- encoding: utf-8 -*-
"""
Local Authorities downloader class
"""

import errno, logging, os

from postcode_api.caches.s3_cache import S3Cache
from postcode_api.caches.filesystem_cache import FilesystemCache
from postcode_api.caches.multi_level_caching_strategy import MultiLevelCachingStrategy
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
        self.caches = [
            FilesystemCache(dir=self.dest_dir),
            S3Cache()
        ]
        self.caching_strategy = kwargs.pop('caching_strategy',
                                           MultiLevelCachingStrategy(caches=self.caches))
        self.cache_key = 'dev-local-authorities'
        self.http_dl = HttpDownloader(self._authoritative_url())
        
    def download(self, destination_dir=None):
        destination_dir = destination_dir or self.dest_dir
        self._make_sure_path_exists(destination_dir)

        cached = self.caching_strategy.get(self.cache_key, self._local_filepath())
        if cached:
            log.info("found in cache!")
            return cached
        else:
            return self._uncached_download()

    def _local_filepath(self):
        filename = self.http_dl.attachment_filename()
        return os.path.join(self.dest_dir, filename)

    def _uncached_download(self):
        log.info("not in cache - downloading")
        downloaded_paths = self.http_dl.download(self.dest_dir)
        for downloaded_path in downloaded_paths:
            log.info("putting to cache with key {key}".format(key=self.cache_key))
            self.caching_strategy.put(self.cache_key, downloaded_path)
    
        return downloaded_paths

    def _make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
