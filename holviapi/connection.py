# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible
import requests


@python_2_unicode_compatible
class Connection(object):
    base_url_fmt = "https://holvi.com/api/"
    session = None
    
    def __init__(self, poolname, authkey):
        self.pool = poolname
        self.key = authkey

    def make_get(self, url, params={}):
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % self.key
            })
        r = self.session.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def make_post(self, url, params, method='POST'):
        raise NotImplementedError()
