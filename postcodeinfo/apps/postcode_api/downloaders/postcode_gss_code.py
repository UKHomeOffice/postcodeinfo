# -*- encoding: utf-8 -*-
"""
Postcode GSS code downloader class
"""

import requests

from .filesystem import LocalCache
from .http import HttpDownloader
from .s3 import S3Cache


class PostcodeGssCodeDownloader(LocalCache, S3Cache, HttpDownloader):

    def __init__(self):
        super(PostcodeGssCodeDownloader, self).__init__(None)
        self.index_url = (
            'https://geoportal.statistics.gov.uk/geoportal'
            '/rest/find/document?searchText=NSPL&f=pjson')

    def download(self, dest_dir=None):
        """
        Fetch the URL of the latest NSPL CSV and download it.
        """

        index = requests.get(self.index_url).json()

        def is_nspl_record(record):
            return record['title'].startswith(
                'National Statistics Postcode Lookup (UK)')

        nspl_records = filter(is_nspl_record, index['records'])

        def updated(record):
            return record['updated']

        newest_record = sorted(nspl_records, key=updated, reverse=True)[0]

        def is_file_link(link):
            return link['type'] == 'open'

        link = filter(is_file_link, newest_record['links'])[0]
        self.url = link['href']

        return super(PostcodeGssCodeDownloader, self).download(
            dest_dir=dest_dir)
