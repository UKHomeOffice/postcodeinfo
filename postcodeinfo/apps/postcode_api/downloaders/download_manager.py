import requests
import os
import pytz

from time import time, gmtime, strftime, strptime, mktime, localtime
from datetime import datetime
from dateutil import parser

from postcode_api.models import Download


class DownloadManager(object):

    def download_if_needed(self, url, dirpath, force=False):
        headers = self.get_headers(url)
        if isinstance(headers, list):
            headers = headers[0]

        download_record = self.existing_download_record(url, headers)
        if self.download_is_needed(download_record) == True or force:
            return self.do_download(url, dirpath, headers)
        else:
            print 'no download needed'
            return None

    def do_download(self, url, dirpath, headers):
        local_path = self.download_to_dir(url, dirpath, headers)
        download_record = self.record_download(url, dirpath, headers)
        return download_record.local_filepath

    def download_to_dir(self, url, dirpath, headers):
        filepath = self.filename(dirpath, url)
        print 'downloading file from ' + url + ' to ' + filepath
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
                    print '{0} bytes of {1}'.format(count*chunk_size,
                                                    content_length)
                count = count + 1
                fd.write(chunk)

        print "downloaded to " + filepath
        return filepath

    def get_headers(self, url):
        r = requests.head(url, allow_redirects=True)
        if isinstance(r.headers, list):
            return r.headers[0]
        else:
            return r.headers

    def _format_time_for_orm(self, given_time):
        obj = None
        # is it a string?
        if isinstance(given_time, basestring):
            obj = parser.parse(given_time)
        else:
            obj = datetime.fromtimestamp(mktime(given_time))

        if obj.tzinfo is None:
            obj = pytz.UTC.localize(obj)

        return obj

    def record_download(self, url, dirpath, headers={}):
        # create Download record storing the url, local path, last modified
        # date, and etag
        formatted_time = self._format_time_for_orm(headers['last-modified'])
        dl = Download(url=url,
                      etag=headers['etag'],
                      last_modified=formatted_time)
        dl.local_filepath = self.filename(dirpath, url)
        dl.state = 'downloaded'
        now = self._format_time_for_orm(localtime())
        dl.last_state_change = now
        dl.save()

        return dl

    def download_is_needed(self, download_record):
        """ Basic naive strategy - if there's an existing record, we don't
            need to re-download. (The existing record is found by the
            combination of url, etag and last_modified, so if and only if
            those three match, then we don't need to download).
            This is sufficient for MVP 1 - future implementations can be as
            complex as needed. """

        if download_record:
            return False
        else:
            # no existing record => download is needed
            return True

    def existing_download_record(self, url, headers):
        last_modified = self._format_time_for_orm(headers['last-modified'])
        dl = Download.objects.filter(url=url,
                                     etag=headers['etag'],
                                     last_modified=last_modified).first()
        if dl:
            print 'existing download record found: '
            print '  state: %s since %s' % (dl.state,  dl.last_state_change)
            print '  last_modified: %s' % dl.last_modified
            print '  etag: %s' % dl.etag
            print '  local_filepath: %s' % dl.local_filepath
        return dl

    def filename(self, dirname, url):
        return dirname + url.split('/')[-1]

    def chunk_size(self):
        """Tune this as needed"""
        return int(os.environ.get('DOWNLOAD_CHUNK_SIZE') or 4192)
