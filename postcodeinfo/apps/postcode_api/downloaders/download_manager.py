import logging
import requests
import os
import pytz

from time import mktime
from datetime import datetime
from dateutil import parser


from postcode_api.downloaders.s3_adapter import S3Adapter


class DownloadManager(object):

    def retrieve(self, url, local_dir_path, force=False):
        """
        Reasons for this workflow:
        1. Ordnance Survey only gives us AddressBase files
           for a limited time after updates are released(21 days)
           then it removes the file from their FTP server

        2. Our release process re-creates an entirely new
           docker container each time, so we can't just
           cache the files locally
        """

        remote_timestamp = self.get_last_modified(url)
        local_file_path = self.filename(local_dir_path, url)

        # if we have an up-to-date local copy, there's nothing to do
        if not self.local_copy_up_to_date(local_file_path, remote_timestamp):
            self.get_from_s3(local_file_path, url, remote_timestamp)

        return local_file_path

    def get_from_s3(self, local_file_path, url, remote_timestamp):
        s3 = self.s3_adapter()
        s3_key = s3.key(url)
        s3_object = s3.file(s3_key)

        if self.s3_object_is_up_to_date(s3_object, remote_timestamp):
            logging.info(
                'downloading from s3 to {path}'.format(path=local_file_path))
            s3.download(s3_object, local_file_path)
        else:
            logging.info(
                'downloading from {url} to {path}'.format(
                    url=url,
                    path=local_file_path))
            self.download_to_file(url, local_file_path)

            logging.info('uploading from {path} to s3 key {key}'.format(
                path=local_file_path, key=s3_key))
            s3.upload(local_file_path, s3_key)

    def s3_adapter(self):
        return S3Adapter()

    def get_last_modified(self, url):
        headers = self.get_headers(url)
        if isinstance(headers, list):
            headers = headers[0]

        return self.format_time_for_orm(headers['last-modified'])

    def local_copy_up_to_date(self, local_file_path, remote_timestamp):
        local_copy = self._in_local_storage(local_file_path)
        if local_copy:
            local_mod_time = os.path.getmtime(local_file_path)
            formatted_mod_time = self.format_time_for_orm(
                local_mod_time)
            result = self.up_to_date(formatted_mod_time, remote_timestamp)
            return result

        return False

    def _in_local_storage(self, local_path):
        return os.path.exists(local_path)

    def up_to_date(self, copy_timestamp, source_timestamp):
        return copy_timestamp >= source_timestamp

    def s3_object_is_up_to_date(self, s3_object, remote_timestamp):
        if s3_object is not None:
            mod_time_on_s3 = self.format_time_for_orm(s3_object.last_modified)
            return self.up_to_date(mod_time_on_s3, remote_timestamp)

        return False

    def download_to_dir(self, url, dirpath, headers):
        filepath = self.filename(dirpath, url)
        logging.info(
            'downloading file from {url} to {path}'.format(
                url=url, path=filepath))
        chunk_size = self.chunk_size()
        content_length = headers['content-length']
        return self.download_to_file(url, filepath, chunk_size, content_length)

    def download_to_file(self,
                         url, filepath,
                         chunk_size=4192,
                         content_length=None):
        r = requests.get(url, stream=True)

        with open(filepath, 'wb') as fd:
            count = 0
            for chunk in r.iter_content(chunk_size):
                if content_length and count % 100 == 0:
                    logging.debug('{0} bytes of {1}'.format(
                        count*chunk_size,
                        content_length))
                count = count + 1
                fd.write(chunk)

        logging.info("downloaded to {path}".format(path=filepath))
        return filepath

    def get_headers(self, url):
        r = requests.head(url, allow_redirects=True)
        if isinstance(r.headers, list):
            return r.headers[0]
        else:
            return r.headers

    def format_time_for_orm(self, given_time):
        obj = None
        # is it a string?
        if isinstance(given_time, basestring):
            obj = parser.parse(given_time)
        elif isinstance(given_time, float):
            obj = datetime.fromtimestamp(given_time)
        else:
            obj = datetime.fromtimestamp(mktime(given_time))

        if obj.tzinfo is None:
            obj = pytz.UTC.localize(obj)

        return obj

    def filename(self, dirname, url):
        return dirname + url.split('/')[-1]

    def chunk_size(self):
        """Tune this as needed"""
        return int(os.environ.get('DOWNLOAD_CHUNK_SIZE') or 4192)
