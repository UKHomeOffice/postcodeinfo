import ftplib
import glob
import logging
import os

from postcode_api.downloaders.download_manager import DownloadManager
from postcode_api.downloaders.ftp_download_manager import FTPDownloadManager
from postcode_api.downloaders.s3_adapter import S3Adapter


class AddressBaseBasicDownloader(object):

    """
    Ordnance Survey very kindly remove the files from our
    FTP area 21 days after they are first put there, despite
    there not being an update available for maybe another 2 months.
    So if we try to cd to our order dir
    and it's not there, we'll end up here.
    So, we then look for a load of csv.zip files in local_dir
    If there are csv.zip files locally, return them
    If not, look on s3.
    If they're on s3, download them and return the local paths.
    Otherwise FAIL
    """

    def __init__(self, dl_mgr=FTPDownloadManager()):
        self.download_manager = dl_mgr

    def download(self, local_dir='/tmp/', force=False):

        self.download_manager.open(
            'osmmftp.os.uk', self._username(), self._password())

        try:
            self.ftp_client().cwd(self._source_dir())
            return self.download_manager.download_all_if_needed(
                './*_csv.zip',
                local_dir,
                force)
        except ftplib.error_perm:
            logging.warning('FTP error - looking for local files')
            return self.local_files(local_dir) or self.files_from_s3(local_dir)

    def ftp_client(self):
        return self.download_manager.ftp_client

    def _username(self):
        username = os.environ.get('OS_FTP_USERNAME')
        if not username:
            logging.error('OS_FTP_USERNAME not set!')

        return username

    def _password(self):
        pwd = os.environ.get('OS_FTP_PASSWORD')
        if not pwd:
            logging.error('OS_FTP_PASSWORD not set!')

        return pwd

    def _source_dir(self):
        # TODO - this is currently just the order number.
        # Make this dynamic based on the most recent directory?
        return os.environ.get('OS_FTP_ORDER_DIR', '../from-os/DCS0001654526/')

    def local_files(self, local_dir):
        files = glob.glob(os.path.join(local_dir, '*csv.zip'))
        logging.debug(
            'found {num_files} files in {path} matching {pattern}'.format(
                num_files=len(files), path=local_dir, pattern='*csv.zip'))
        return files

    def files_from_s3(self, local_dir):
        files = []
        s3 = S3Adapter()
        s3_files = s3.bucket.list('AddressBase')
        logging.debug('found %i files in s3 matching %s' %
                      (len(s3_files), 'AddressBase'))
        for key in s3_files:
            logging.debug('downloading %s' % key.name)
            files.append(s3.download(key, os.path.join(local_dir, key.name)))

        return files
