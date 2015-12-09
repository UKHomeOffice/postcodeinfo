import logging
import os
import errno

from postcode_api.caches.filesystem_cache import FilesystemCache
from postcode_api.caches.s3_cache import S3Cache
from postcode_api.caches.multi_level_caching_strategy import MultiLevelCachingStrategy


log = logging.getLogger(__name__)


class DownloadManager(object):

    def __init__(self, *args, **kwargs):
        self.destination_dir = kwargs.pop('destination_dir', '/tmp/')
        self.caching_strategy = kwargs.pop(
            'caching_strategy', self._default_caching_strategy())
        self.downloader = kwargs.pop('downloader')

    def download(self, *args, **kwargs):
        url = kwargs.pop('url')
        filename = kwargs.pop('filename', url.split('/')[-1])
        cache_key = kwargs.pop('cache_key', filename)
        dest_dir = kwargs.pop('dest_dir', self.destination_dir)
        local_filepath = os.path.join(dest_dir, filename)

        self._make_sure_path_exists(dest_dir)
        cached = self.caching_strategy.get(cache_key, local_filepath)
        if cached:
            log.info("found in cache!")
            return cached
        else:
            return self.download_and_put_to_cache(cache_key, dest_dir)

    def download_and_put_to_cache(self, cache_key, dest_dir=None):
        dest_dir = dest_dir or self.destination_dir
        log.info("not in cache - downloading")
        downloaded_paths = self.downloader.download(
            pattern=cache_key, dest_dir=dest_dir)
        for downloaded_path in downloaded_paths:
            log.info("putting to cache with key {key}".format(key=cache_key))
            self.caching_strategy.put(cache_key, downloaded_path)

        return downloaded_paths

    def download_all_matching(self, *args, **kwargs):
        pattern = kwargs.pop('pattern')
        files = self.downloader.list(pattern)
        log.debug('{n} files matching {pattern}'.format(
            n=len(files), pattern=pattern))

        downloaded = []
        for this_file in files:
            log.info('downloading {file}'.format(file=this_file))
            #src_file = os.path.join(self.destination_dir, this_file.split('/')[-1])
            self.downloader.url = this_file
            downloaded.append(
                self.download(url=this_file, dest_dir=self.destination_dir))

        return downloaded

    def _make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def _default_caching_strategy(self):
        caches = [
            FilesystemCache(),
            S3Cache()
        ]
        return MultiLevelCachingStrategy(caches=caches)

