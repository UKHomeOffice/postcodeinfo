import ftplib
import re

from dateutil import parser
from ftplib import FTP

from postcode_api.downloaders.download_manager import DownloadManager

class FTPDownloadManager(DownloadManager):

  def __init__(self):
    self.ftp_client = None;

  def open(self, host, username, password):
    if self.ftp_client:
      self.ftp_client.close()
    
    self.ftp_client = FTP(host)
    self.ftp_client.login(username, password)
    return self.ftp_client

  def list_files(self, pattern):
    """ pattern to match against files (e.g. subdir/*.csv) or '.' """
    headers = self.get_headers(pattern)
    return map( lambda f: f['url'], headers )

  def download_all_if_needed(self, pattern, dirpath, force=False):
    files = self.list_files(pattern)
    downloads = []
    print '%i files matching %s' % (len(files), pattern)
    for file in files:
      dl = self.download_if_needed(file, dirpath, force)
      if dl:
        downloads.append(dl)

    return "\n".join( map( lambda dl: dl.local_filepath, downloads ) )

  def get_headers(self, pattern=None):
    files_in_dir = []
    self.ftp_client.dir(pattern, lambda f: files_in_dir.append(f))

    headers = map(lambda f: self.interpret_ls_line(f), files_in_dir)
    return headers

  def interpret_ls_line(self, line):
    """ NOTE: this is VERY brittle, but the OS FTP server doesn't
        support the MSLD command (which is intended to produce
        machine-readable output) so we don't have many other options.
        Here we're trying to emulate as closely as possible the headers
        that we would get back from a HTTP HEAD request
    """
    cols = re.split(' +', line)

    dic = {
      'permissions': cols[0],
      'content-length': int(cols[4]),
      'last-modified': ' '.join(cols[5:8]),
      'url': cols[-1],
      'etag': None
    }
    return dic

  def download_to_dir(self, url, dirpath, headers):
    filepath = self.filename(dirpath, url)
    print 'downloading file from ' + url + ' to ' + filepath

    file = open(filepath, 'wb')
    counts = { 'size': 0, 'chunks': 0 }

    # defined as a local closure so that it can access the variables in local scope
    # We have to do it this way because:
    # a) the ftplib interface only supports one argument to the named callback 
    # b) you can't reassign a primitive inside a closure, but you *can* 
    #    mutate a key in a dict. This is .... not pleasant, but it works.
    def handle_chunk_callback(data):
      counts['size'] += len(data)
      counts['chunks'] += 1
      file.write(data)
      if counts['chunks'] % 100 == 0:
        print '%i/%i bytes' % (counts['size'], headers['content-length'])
    
    self.ftp_client.retrbinary( 'RETR %s' % url, handle_chunk_callback )

    print "downloaded to " + filepath
    return filepath
