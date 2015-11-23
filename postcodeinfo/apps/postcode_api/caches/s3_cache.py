# -*- encoding: utf-8 -*-
"""
S3-based Cache implementation
"""

import logging

import boto
from boto.s3.key import Key
from dateutil import parser as dateparser
from django.conf import settings
import pytz

from postcode_api.caches.cache import Cache


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

    def key_for(self, object_identifier):
        """ 
        S3 can handle filenames with slash-separators transparently
        """
        return object_identifier

    def _s3_key(self, cache_key):
        return Key(self.bucket, self.key_for(cache_key))

    def has(self, cache_key):
        return self._s3_key(cache_key).exists()

    def get(self, cache_key, dest_filename):
        return self._s3_key(cache_key).get_contents_to_filename(dest_filename)

    def put(self, filename):
        s3_key = self._s3_key(self.key_for(filename))
        return s3_key.set_contents_from_filename(filename)

    def delete(self, cache_key):
        return self._s3_key(cache_key).delete()

    def last_modified(self, cache_key):
        return self._s3_key(cache_key).last_modified