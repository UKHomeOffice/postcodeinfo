import logging
import requests
import urllib
import urlparse


class GenuineApi(object):

    def __init__(self, root_url=None, auth_token=None):
        self.root_url = root_url
        self.auth_token = auth_token

    def _full_url(self, endpoint):
        url = urlparse.urljoin(self.root_url, endpoint)
        params = {'token': self.auth_token, 'format': 'json'}

        url_parts = list(urlparse.urlsplit(url))

        query_dict = dict(urlparse.parse_qsl(url_parts[3]))
        url_parts[3] = urllib.urlencode(dict(query_dict, **params))

        return urlparse.urlunsplit(url_parts)

    def get(self, endpoint):
        api_url = self._full_url(endpoint)
        logging.debug('hitting ' + api_url)
        return requests.get(api_url)
