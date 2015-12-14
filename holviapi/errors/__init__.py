# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible
from requests.exceptions import HTTPError, Timeout

@python_2_unicode_compatible
class HolviError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(HolviError, self).__init__(*args, **kwargs)

class ApiError(HTTPError, HolviError):
    def __init__(self, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)

class AuthenticationError(ApiError):
    def __init__(self, *args, **kwargs):
        super(AuthenticationError, self).__init__(*args, **kwargs)

class ApiTimeout(ApiError, Timeout):
    def __init__(self, *args, **kwargs):
        super(ApiTimeout, self).__init__(*args, **kwargs)

