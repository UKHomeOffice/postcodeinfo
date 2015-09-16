# -*- encoding: utf-8 -*-
"""
Local Authorities downloader class
"""

import os

from .filesystem import LocalCache
from .http import HttpDownloader
from .s3 import S3Cache


class LocalAuthoritiesDownloader(LocalCache, S3Cache, HttpDownloader):

    def _authoritative_url(self):
        default_url = 'http://opendatacommunities.org/downloads/graph?uri='\
                      'http://opendatacommunities.org/graph/dev-'\
                      'local-authorities'

        return os.environ.get('LOCAL_AUTHORITIES_DUMP_URL') or default_url

    def __init__(self):
        super(LocalAuthoritiesDownloader, self).__init__(
            self._authoritative_url())
