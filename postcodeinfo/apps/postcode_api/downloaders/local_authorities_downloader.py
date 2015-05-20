
from .download_manager import DownloadManager


class LocalAuthoritiesDownloader(object):

    def download(self, target_dir='/tmp/', force=False):
        most_recent_file_url = self.__target_href()

        dl_mgr = DownloadManager()

        return dl_mgr.download_if_needed(most_recent_file_url,
                                         target_dir,
                                         force)

    def __target_href(self):
        return 'http://opendatacommunities.org/data/dev-local-authorities/dump'
