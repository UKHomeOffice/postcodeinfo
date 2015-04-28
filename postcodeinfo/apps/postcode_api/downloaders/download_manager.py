import requests
import os

from time import time, gmtime, strftime, strptime, mktime, localtime
from datetime import datetime
from dateutil import parser

from postcode_api.models import Download

class DownloadManager(object):

  def download_if_needed(self, url, dirpath):
    headers = get_headers(url)
    print 'headers = '
    print headers

    download_record = self.existing_download_record(url, headers)
    if self.download_is_needed(download_record):
      local_path = self.download_to_dir(url, dirpath, headers)
      download_record = self.record_download(url, dirpath, headers)
      return download_record
    else:
      print 'no download needed'
      return download_record

  def download_to_dir(self, url, dirpath, headers):
    filepath = self.filename(dirpath, url)
    print 'downloading file from ' + url + ' to ' + filepath
    r = requests.get(url, stream=True)
    chunk_size = self.chunk_size()
    content_length = headers['content-length']

    with open(filepath, 'wb') as fd:
      count = 0
      for chunk in r.iter_content(chunk_size):
          count = count + 1
          if count % 100 == 0 :
            print '{0} bytes of {1}'.format(count*chunk_size, content_length)
          fd.write(chunk)

    print "downloaded to " + filepath
    return filepath

  def __get_headers(self, url):
    requests.head(url, allow_redirects=True).headers

  def __format_time_for_orm(self, given_time):
    # is it a string?
    if str(given_time) == given_time:
        obj = parser.parse(given_time)
        return obj
    else:
      return datetime.fromtimestamp(mktime(given_time))
      #return given_time.strftime( 'YYYY-mm-dd HH:MM:SS' )

  def record_download(self, url, dirpath, headers={}):
    # create Download record storing the url, local path, last modified date, and etag
    dl = Download(url=url, etag=headers['etag'], 
              last_modified=self.__format_time_for_orm(headers['last-modified']) )
    dl.local_filepath = self.filename( dirpath, url )
    dl.state = 'downloaded'
    dl.last_state_change = self.__format_time_for_orm( localtime() )
    #import pdb; pdb.set_trace()
    dl.save()

    return dl

  def download_is_needed(self, download_record):
    """ Basic naive strategy - if there's an existing record, we don't
        need to re-download. (The existing record is found by the combination
        of url, etag and last_modified, so if and only if those three match,
        then we don't need to download).
        This is sufficient for MVP 1 - future implementations can be as
        complex as needed. """

    if download_record:
      print 'existing download record found: '
      print '  state: %s since %s' % ( download_record.state,  download_record.last_state_change) 
      print '  last_modified: %s' % download_record.last_modified
      print '  etag: %s' % download_record.etag
      print '  local_filepath: %s' % download_record.local_filepath
      return False
    else:
      # no existing record => download is needed
      return True

  def existing_download_record(self, url, headers):
    dl = Download.objects.filter(url=url, etag=headers['etag'], last_modified=parser.parse(headers['last-modified'])).first()
    return dl

  def filename(self, dirname, url):
    return dirname + url.split('/')[-1]

  def chunk_size(self):
    """Tune this as needed"""
    return os.environ.get('DOWNLOAD_CHUNK_SIZE', 4192)