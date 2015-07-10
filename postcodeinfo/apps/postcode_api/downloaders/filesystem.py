# -*- encoding: utf-8 -*-
"""
Local filesystem downloader cache mixin class
"""

import datetime
import os
from os.path import exists, getmtime
from time import mktime

import pytz


def last_modified(filename):
    """
    Get the last modified datetime of the specified file
    """

    mtime = getmtime(filename)
    if os.stat_float_times():
        dt = datetime.datetime.fromtimestamp(mtime)
    else:
        dt = datetime.datetime.fromtimestamp(mktime(mtime))
    return pytz.UTC.localize(dt)


class LocalCache(object):
    """
    Download files unless they already exist locally and are newer than the
    files on the server.
    """

    def download_file(self, src, dest):
        """
        Download a single file, unless the file already exists locally and is
        newer than the remote file.
        """

        if exists(dest) and last_modified(dest) >= self.last_modified(src):
            return dest

        return super(LocalCache, self).download_file(src, dest)
