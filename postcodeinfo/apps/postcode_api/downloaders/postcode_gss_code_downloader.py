import os
import requests
import json

from .download_manager import DownloadManager


class PostcodeGssCodeDownloader(object):

    def download(self, target_dir='/tmp/', force=False):
        most_recent_file_url = self._target_href()

        dl_mgr = DownloadManager()
        return dl_mgr.download_if_needed(most_recent_file_url,
                                         target_dir,
                                         force)

    def _target_href(self):
        index_json = requests.get(self._index_json_url()).text
        index = json.loads(index_json)

        return self._get_most_recent_file_url(index)

    def _get_most_recent_file_url(self, parsed_index):
        nspl_elements = filter(
            self._is_nspl_csv_link, parsed_index['records'])
        most_recent = sorted(
            nspl_elements, key=lambda e: e['updated'], reverse=True)[0]
        return self._file_url(most_recent['links'])

    def _index_json_url(self):
        return 'https://geoportal.statistics.gov.uk/geoportal'\
            '/rest/find/document?searchText=NSPL&f=pjson'

    def _is_nspl_csv_link(self, element):
        return element['title'].startswith(
            'National Statistics Postcode Lookup (UK)')

    def _file_url(self, links):
        link = filter(self._is_file_link, links)[0]
        return link['href']

    def _is_file_link(self, link):
        return link['type'] == 'open'
