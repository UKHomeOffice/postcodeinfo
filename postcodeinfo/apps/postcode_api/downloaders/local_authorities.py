# -*- encoding: utf-8 -*-
"""
Local Authorities downloader class
"""

import logging
import os
import re
import requests

from ..caches.s3_cache import S3Cache
from ..caches.filesystem_cache import FilesystemCache
from ..caches.multi_level_caching_strategy import MultiLevelCachingStrategy
from ..downloaders.download_manager import DownloadManager

from .http import HttpDownloader
#from .s3 import S3Cache

log = logging.getLogger(__name__)


class LocalAuthoritiesDownloader():

    def _index_url(self):
        return os.environ.get('LOCAL_AUTHORITIES_INDEX_URL',
                              ("http://geoportal.statistics.gov.uk/geoportal/"
                               "rest/find/document?searchText="
                               "Local%20Authority%20Districts%20UK&f=pjson"))

    def _get_latest_file_url(self):
        index = requests.get(self._index_url()).json()
        la_records = filter(
            self._is_uk_local_authorities_list, index['records'])
        newest_record = sorted(
            la_records, key=self._year_from_title, reverse=True)[0]
        return filter(self._is_file_link, newest_record['links'])[0]

    def _is_file_link(self, link):
        return link['type'] == 'open'

    def _is_uk_local_authorities_list(self, record):
        title = record['title'].lower()
        pattern = 'local authority districts \(uk\) .* names and codes'
        return re.search(pattern, title)

    def _year_from_title(self, record):
        pattern = ('local authority districts \(uk\)'
                   '.*([0-9]+).* names and codes')
        return re.sub(pattern, '\1', record['title'])

    def __init__(self, *args, **kwargs):
        self.dest_dir = kwargs.pop('destination_dir', '/tmp/local_authorities')

        self.cache_key = 'local-authorities-names-to-codes'

    def download(self, dest_dir):
        url = self._get_latest_file_url()['href']

        dl_mgr = DownloadManager(
            destination_dir=dest_dir,
            downloader=HttpDownloader(url),
            caching_strategy=self._caching_strategy())
        return dl_mgr.download(url=url)

    def _caching_strategy(self):
        caches = [
            FilesystemCache(dir='/tmp/local_authorities'),
            S3Cache()
        ]
        return MultiLevelCachingStrategy(caches=caches)
