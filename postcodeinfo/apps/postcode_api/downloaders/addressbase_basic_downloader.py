

from .download_manager import DownloadManager

class AddressBaseBasicDownloader(object):

  def download(self, target_dir='/tmp/'):

    dl_mgr = FTPDownloadManager()
    dl_mgr.open('osmmftp.os.uk', self.__username, self.__password)
    dl_mgr.ftp_client.cwd(self.__target_dir())

    most_recent_file_urls = dl_mgr.headers('*.zip')

    return dl_mgr.download_if_needed(most_recent_file_url, target_dir)


  def __username(self):
    return os.environ.get('OS_FTP_USERNAME')

  def __password(self):
    return os.environ.get('OS_FTP_PASSWORD')
    
  def __target_dir(self):
    return '../from-os/DCS0001654526'
