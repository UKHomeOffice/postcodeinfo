# -*- encoding: utf-8 -*-
"""
Local Authorities downloader class
"""

from .filesystem import LocalCache
from .http import HttpDownloader
from .s3 import S3Cache


class LocalAuthoritiesDownloader(LocalCache, S3Cache, HttpDownloader):

    def __init__(self):
        super(LocalAuthoritiesDownloader, self).__init__(
            'http://opendatacommunities.org/data/dev-local-authorities/dump')
