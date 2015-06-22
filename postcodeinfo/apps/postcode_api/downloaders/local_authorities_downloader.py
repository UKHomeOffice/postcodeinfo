
from .download_manager import DownloadManager


class LocalAuthoritiesDownloader(object):

    def download(self, target_dir='/tmp/', force=False):
        most_recent_file_url = self._target_href()

        dl_mgr = DownloadManager()

        return dl_mgr.retrieve(most_recent_file_url,
                               target_dir,
                               force)

    def _target_href(self):
        return 'http://opendatacommunities.org/data/dev-local-authorities/dump'
