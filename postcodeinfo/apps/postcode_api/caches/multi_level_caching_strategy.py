# -*- encoding: utf-8 -*-
"""
MultiLevelCachingStrategy
Will look for the given filename in local cache, then S3

"""

class MultiLevelCachingStrategy:

    def __init__(self, *args, **kwargs):
        self.caches = kwargs.pop('caches', [])

    def get(self, filename, dest_filename):
        for cache in self.caches:
            key = cache.key_for(filename)
            if cache.has(key):
                return cache.get(key, dest_filename)

        # if we get here, then no cache has the file
        # and so we don't return anything


