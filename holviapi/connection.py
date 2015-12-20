# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
import six
import json
import requests
from requests.exceptions import HTTPError, Timeout
import requests_cache
from .errors import AuthenticationError, ApiError, ApiTimeout

# Cache GET results for 5min to save Holvis bandwidth (also the API is a bit on the slow side so this makes things faster for us)
requests_cache.install_cache('Holvi-REST', 'memory', expire_after=300)

@python_2_unicode_compatible
class Connection(object):
    base_url_fmt = "https://holvi.com/api/"
    session = None
    
    def __init__(self, poolname, authkey):
        self.pool = poolname
        self.key = authkey

    def _init_session(self):
        """Iniitializes a requests.Session for us if not already initialized"""
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': 'Token %s' % self.key
            })

    def make_get(self, url, params={}):
        """Make a GET request"""
        self._init_session()
        r = self.session.get(url, params=params)
        try:
            r.raise_for_status()
        except Timeout as e:
            raise ApiTimeout(six.u(e), response=e.response)
        except HTTPError as e:
            if e.response.status_code in (403, 401):
                raise AuthenticationError(six.u(e), response=e.response)
            else:
                raise ApiError(six.u(e), response=e.response)
        return r.json()

    def make_post(self, url, payload):
        """Make a POST request"""
        return self._make_ppp('post', url, payload)

    def make_put(self, url, payload):
        """Make a PUT request"""
        return self._make_ppp('put', url, payload)

    def make_patch(self, url, payload):
        """Make a PATCH request"""
        return self._make_ppp('patch', url, payload)

    def _make_ppp(self, method, url, payload):
        """Internal helper to make POST/PUT/PATCH requests (or whatever the underlying library supports)"""
        self._init_session()
        # We can't trust the cache after we have made changes of our own
        requests_cache.clear()
        m = getattr(self.session, method)
        r = m(url, data=json.dumps(payload))
        try:
            r.raise_for_status()
        except Timeout as e:
            raise ApiTimeout(six.u(e), response=e.response)
        except HTTPError as e:
            if e.response.status_code in (403, 401):
                raise AuthenticationError(six.u(e), response=e.response)
            else:
                raise ApiError(six.u(e), response=e.response)
        return r.json()
