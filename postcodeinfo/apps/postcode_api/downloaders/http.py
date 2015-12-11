# -*- encoding: utf-8 -*-
"""
HTTP downloader class
"""

from dateutil import parser as dateparser

import cgi
import logging
import os
import pytz
import requests
import tempfile


log = logging.getLogger(__name__)


class HttpDownloader(object):

    """
    Downloads files from a HTTP server.
    """

    def __init__(self, url):
        self.url = url
        self.chunk_size = int(os.environ.get('DOWNLOAD_CHUNK_SIZE', 4192))
        self._headers = {}

    def download(self, *args, **kwargs):
        """
        Execute the download.
        Returns a list of downloaded files.
        """
        dest_dir = kwargs.pop(
            'dest_dir', tempfile.mkdtemp(prefix=self.__class__.__name__))
        url = kwargs.pop('url', self.url)
        dest = os.path.join(dest_dir, url.split('/')[-1])
        return [self.download_file(url, dest)]

    def download_file(self, src, dest):
        """
        Download a single file.
        """

        def download():
            log.debug('downloading {src} to {dest}'.format(
                src=src, dest=dest))
            data = requests.get(src, stream=True)
            with open(dest, 'wb') as f:
                for i, chunk in enumerate(data.iter_content(self.chunk_size)):
                    f.write(chunk)
                    yield i

        log.debug('downloading {src} to {dest}'.format(
            src=src, dest=dest))

        content_length = self._get_headers(src).get('content-length')

        for chunk in download():
            if chunk % 100 == 0:
                log.debug('{0} bytes of {1}'.format(
                    chunk * self.chunk_size, content_length))

        log.info('downloaded {dest}'.format(dest=dest))

        return dest

    def _get_headers(self, src):
        if src not in self._headers:
            r = requests.head(src, allow_redirects=True)
            self._headers[src] = r.headers
        return self._headers[src]

    def attachment_filename(self, headers=None):
        if headers == None:
            headers = self._get_headers(self.url)
        disposition, value = cgi.parse_header(headers['Content-Disposition'])
        return value['filename']

    def last_modified(self, src=None):
        """
        Get the last modified datetime of the remote file
        """

        if src is None:
            src = self.url
        hdrs = self._get_headers(src)
        if hdrs.get('last-modified'):
            dt = dateparser.parse(hdrs['last-modified'])
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            return dt
