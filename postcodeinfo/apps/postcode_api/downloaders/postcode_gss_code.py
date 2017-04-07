# -*- encoding: utf-8 -*-
"""
Postcode GSS code downloader class
"""

import requests

from .http import HttpDownloader

from ..downloaders.download_manager import DownloadManager
from ..caches.s3_cache import S3Cache
from ..caches.filesystem_cache import FilesystemCache
from ..caches.multi_level_caching_strategy import MultiLevelCachingStrategy


class PostcodeGssCodeDownloader(object):

    def __init__(self, *args, **kwargs):
        self.index_url = (
            'http://geoportal.statistics.gov.uk/geoportal'
            '/rest/find/document?searchText=NSPL&max=100&f=pjson')
        self.dest_dir = kwargs.pop(
            'destination_dir', '/tmp/postcode_gss_codes')
        self.cache_key = 'postcode_gss_codes'

    def download(self, dest_dir):
        """
        Fetch the URL of the latest NSPL CSV and download it.
        """

        url = self.get_file_link()['href']
        dl_mgr = DownloadManager(
            destination_dir=dest_dir, downloader=HttpDownloader(url),
            caching_strategy=self._caching_strategy())

        return dl_mgr.download(url=url)

    def get_file_link(self):
        index = requests.get(self.index_url).json()

        nspl_records = filter(self.is_nspl_record, index['records'])
        newest_record = sorted(nspl_records, key=self.updated, reverse=True)[0]
        return filter(self.is_file_link, newest_record['links'])[0]

    def is_file_link(self, link):
        return link['type'] == 'open'

    def updated(self, record):
        return record['updated']

    def is_nspl_record(self, record):
        return record['title'].startswith(
            'National Statistics Postcode Lookup (UK)')

    def _caching_strategy(self):
        caches = [
            FilesystemCache(dir='/tmp/local_authorities'),
            S3Cache()
        ]
        return MultiLevelCachingStrategy(caches=caches)
