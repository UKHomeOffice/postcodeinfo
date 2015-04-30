import os

from .download_manager import DownloadManager
from .ftp_download_manager import FTPDownloadManager

class AddressBaseBasicDownloader(object):

  def download(self, target_dir='/tmp/'):

    dl_mgr = FTPDownloadManager()
    dl_mgr.open('osmmftp.os.uk', self.__username(), self.__password())
    dl_mgr.ftp_client.cwd(self.__target_dir())

    return dl_mgr.download_all_if_needed('./*_csv.zip', '/tmp/')


  def __username(self):
    return os.environ.get('OS_FTP_USERNAME')

  def __password(self):
    return os.environ.get('OS_FTP_PASSWORD')
    
  def __target_dir(self):
    # TODO - this is currently just the order number.
    # Make this dynamic based on the most recent directory?
    return os.environ.get('OS_FTP_ORDER_DIR', '../from-os/DCS0001654526/')
