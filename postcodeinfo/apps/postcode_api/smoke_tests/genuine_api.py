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
        # the given endpoint might already contain a query string,
        # so we have to do this convoluted dict-merging thing
        # Must use parse_sql as parse_qs raturns each param as a
        # single-element array, which means urlencode then preserves
        # the [] when converting it back to a query string
        qs_as_dict = urlparse.parse_qsl(urlparse.urlsplit(url).query)
        combined_query = urllib.urlencode(
            dict(qs_as_dict + params.items()))
        # ParseResult is immutable, so we have to set the query like this
        url_parts = list(urlparse.urlparse(url))
        url_parts[4] = combined_query

        return urlparse.urlunparse(url_parts)

    def get(self, endpoint):
        u = self._full_url(endpoint)
        print 'hitting ' + u
        return requests.get(u)
