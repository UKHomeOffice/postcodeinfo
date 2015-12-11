# -*- encoding: utf-8 -*-
"""
MultiLevelCachingStrategy
Will look for the given filename in local cache, then S3

"""

import logging


log = logging.getLogger(__name__)


class MultiLevelCachingStrategy:

    def __init__(self, *args, **kwargs):
        self.caches = kwargs.pop('caches', [])

    def get(self, cache_key, dest_filename):
        best = None
        # import pdb; pdb.set_trace()
        for cache in self.caches:
            log.info("looking for {cache_key} in cache {cache}".format(
                cache_key=cache_key, cache=cache))
            if cache.has(cache_key):
                log.info(
                    "found {cache_key} in cache {cache}".format(
                        cache_key=cache_key, cache=cache))
                last_mod = cache.last_modified(cache_key)
                if self.is_newer(last_mod, best):
                    log.info(
                        "better than previous best {best}".format(
                            best=str(best)))
                    best = {'cache': cache,
                            'key': cache_key,
                            'last_modified': cache.last_modified(cache_key)
                            }
            else:
                log.info("cache key {cache_key} not"
                         " found in cache {cache}".format(
                             cache_key=cache_key, cache=cache))
        if best:
            return best['cache'].get(best['key'], dest_filename)

        # if we get here, then no cache has the file
        # and so we don't return anything

    def put(self, cache_key, local_filepath):
        for cache in self.caches:
            log.info('putting {file} to {cache} with key {key}'.format(
                file=local_filepath, cache=str(cache), key=cache_key))
            cache.put(cache_key, local_filepath)

    def is_newer(self, last_modified, best):
        if best and best['last_modified']:
            if last_modified and last_modified > best['last_modified']:
                return True
        else:
            return True

        return False
