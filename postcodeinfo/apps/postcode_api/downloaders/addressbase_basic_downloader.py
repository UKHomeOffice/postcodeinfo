import os

from postcode_api.downloaders.download_manager import DownloadManager
from postcode_api.downloaders.ftp_download_manager import FTPDownloadManager


class AddressBaseBasicDownloader(object):

    def __init__(self, dl_mgr=FTPDownloadManager()):
        self.download_manager = dl_mgr

    def download(self, local_dir='/tmp/', force=False):

        self.download_manager.open(
            'osmmftp.os.uk', self.__username(), self.__password())
        self.download_manager.ftp_client.cwd(self.__source_dir())

        return self.download_manager.download_all_if_needed('./*_csv.zip',
                                                            local_dir,
                                                            force)

    def __username(self):
        username = os.environ.get('OS_FTP_USERNAME')
        if not username:
            print 'OS_FTP_USERNAME not set!'

        return username

    def __password(self):
        pwd = os.environ.get('OS_FTP_PASSWORD')
        if not pwd:
            print 'OS_FTP_PASSWORD not set!'

        return pwd

    def __source_dir(self):
        # TODO - this is currently just the order number.
        # Make this dynamic based on the most recent directory?
        return os.environ.get('OS_FTP_ORDER_DIR', '../from-os/DCS0001654526/')
