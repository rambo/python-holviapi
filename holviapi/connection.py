from __future__ import print_function
from future.utils import python_2_unicode_compatible
import requests


@python_2_unicode_compatible
class Connection(object):
    base_url_fmt = "https://holvi.com/api/"
    
    def __init__(self, poolname, authkey):
        self.pool = poolname
        self.key = authkey

    def make_get(self, url, params={}):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token %s' % self.key
        }
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def make_post(self, url, params, method='POST'):
        raise NotImplementedError()
