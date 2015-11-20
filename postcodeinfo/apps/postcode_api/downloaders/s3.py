# -*- encoding: utf-8 -*-
"""
Downloader mixin class that caches downloads on Amazon S3
"""

import logging

import boto
from boto.s3.key import Key
from dateutil import parser as dateparser
from django.conf import settings
import pytz


log = logging.getLogger(__name__)


class S3Cache(object):

    """
    Download files unless they already exist in S3 and are newer than the files
    on the server.
    """

    def __init__(self, *args, **kwargs):
        self._bucket = None
        self.region_name = kwargs.pop('region', None)
        if self.region_name is None:
            self.region_name = settings.AWS['region_name']
        self.bucket_name = kwargs.pop('bucket', None)
        if self.bucket_name is None:
            self.bucket_name = settings.AWS['s3_bucket_name']
        super(S3Cache, self).__init__(*args, **kwargs)

    @property
    def bucket(self):
        if self._bucket is None:
            conn = boto.s3.connect_to_region(self.region_name)
            self._bucket = conn.get_bucket(self.bucket_name)
        return self._bucket

    def download_file(self, src, dest):
        """
        Download a single file, unless the file already exists in S3 and is
        newer than the remote file - in which case, download from S3.
        """

        key_name = src.split('/')[-1]
        
        try:
            key = self.bucket.get_key(key_name)
        except Exception as e:
            logging.exception('could not get_key {key_name} '
                              'from s3 bucket {bucket_name} '.format(
                                  key_name=key_name,
                                  bucket_name=self.bucket_name))
            return super(S3Cache, self).download_file(src, dest)

        if self._download_needed(src, key):
            log.debug('downloading from s3 key {key_name} to {dest}'.format(
                key_name=key_name, dest=dest))
            key.get_contents_to_filename(dest)
            return dest

        result = super(S3Cache, self).download_file(src, dest)

        self._upload(dest, key_name)

        return result

    def _download_needed(self, src, key):
        src_last_modified = self.last_modified(src)
        dest_last_modified = self._last_modified_with_timezone(key)
        return (key and dest_last_modified and src_last_modified
                and dest_last_modified >= src_last_modified)

    def _upload(self, filename, keyname):
        log.debug('uploading {filename} to s3 key {keyname}'.format(
            keyname=keyname, filename=filename))

        key = Key(self.bucket, keyname)
        try:
            key.set_contents_from_filename(filename)
        except boto.exception.S3ResponseError:
            # ignore problems in the upload as we have the file locally
            pass

    def _last_modified_with_timezone(self, k):
        try:
            dt = dateparser.parse(k.last_modified)
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            return dt
        except:
            pass
