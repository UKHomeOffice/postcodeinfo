# -*- encoding: utf-8 -*-
"""
Filesystem-based Cache implementation
"""
import datetime
import logging
import os
import shutil

import pytz
from os.path import getmtime
from time import mktime

from postcode_api.caches.cache import Cache


class FilesystemCache(Cache):

    def __init__(self, *args, **kwargs):
        self._bucket = None
        self.dir = kwargs.pop('dir', '/tmp/')

    def key_for(self, object_identifier):
        """
        Assumption: we'll be given valid filenames (?)
        """
        return object_identifier

    def _full_path(self, cache_key):
        return os.path.join(self.dir, cache_key)

    def has(self, cache_key):
        return os.path.isfile(self._full_path(cache_key))

    def get(self, cache_key, dest_filename):
        return shutil.copy2(self._full_path(cache_key), dest_filename)

    def put(self, filename):
        shutil.copy2(filename, self._full_path(self.key_for(filename)))

    def delete(self, cache_key):
        return os.remove(self._full_path(cache_key))

    def last_modified(self, cache_key):
        mtime = getmtime(self._full_path(cache_key))
        if os.stat_float_times():
            dt = datetime.datetime.fromtimestamp(mtime)
        else:
            dt = datetime.datetime.fromtimestamp(mktime(mtime))
        return pytz.UTC.localize(dt)
