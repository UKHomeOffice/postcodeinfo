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

log = logging.getLogger(__name__)


class FilesystemCache(Cache):

    def __init__(self, *args, **kwargs):
        self._bucket = None
        self.dir = kwargs.pop('dir', '/tmp/')
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def _full_path(self, cache_key):
        return os.path.join(self.dir, cache_key)

    def has(self, cache_key):
        return os.path.isfile(self._full_path(cache_key))

    def get(self, cache_key, dest_filename):
        if self.has(cache_key):
            return shutil.copy2(self._full_path(cache_key), dest_filename)

    def put(self, cache_key, filename):
        dest_path = self._full_path(cache_key)
        log.info(
            "putting {filename} to filesystem cache with key {key}, full path = {path}"
            .format(filename=filename, key=cache_key, path=dest_path))
        if filename == dest_path:
            log.error("{filename} and {dest_path} are the same - nothing to do!".format(
                filename=filename, dest_path=dest_path))
        else:
            shutil.copy2(filename, dest_path)

    def delete(self, cache_key):
        if self.has(cache_key):
            return os.remove(self._full_path(cache_key))

    def last_modified(self, cache_key):
        mtime = getmtime(self._full_path(cache_key))
        if os.stat_float_times():
            dt = datetime.datetime.fromtimestamp(mtime)
        else:
            dt = datetime.datetime.fromtimestamp(mktime(mtime))
        return pytz.UTC.localize(dt)
