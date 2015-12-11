# -*- encoding: utf-8 -*-
"""
S3-based Cache implementation
"""

import logging

import boto
from django.conf import settings

from .cache import Cache

log = logging.getLogger(__name__)


class S3Cache(Cache):

    def __init__(self, *args, **kwargs):
        self._bucket = None
        self.region_name = kwargs.pop('region', None)
        if self.region_name is None:
            self.region_name = settings.AWS['region_name']
        self.bucket_name = kwargs.pop('bucket', None)
        if self.bucket_name is None:
            self.bucket_name = settings.AWS['s3_bucket_name']

    @property
    def bucket(self):
        if self._bucket is None:
            conn = boto.s3.connect_to_region(self.region_name)
            self._bucket = conn.get_bucket(self.bucket_name)
        return self._bucket

    def _s3_key(self, cache_key):
        return boto.s3.key.Key(self.bucket, cache_key)

    def has(self, cache_key):
        return self._s3_key(cache_key).exists()

    def get(self, cache_key, dest_filename):
        if self.has(cache_key):
            return self._s3_key(cache_key).get_contents_to_filename(
                dest_filename)

    def put(self, key, local_filename):
        s3_key = self._s3_key(local_filename)
        return s3_key.set_contents_from_filename(local_filename)

    def delete(self, cache_key):
        if self.has(cache_key):
            return self._s3_key(cache_key).delete()

    def last_modified(self, cache_key):
        if self.has(cache_key):
            return self._s3_key(cache_key).last_modified
