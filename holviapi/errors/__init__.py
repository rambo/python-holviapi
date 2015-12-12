# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible

@python_2_unicode_compatible
class HolviError(RuntimeError):
    pass

class ApiError(HolviError):
    pass

class AuthenticationError(HolviError):
    pass

class NotFound(HolviError):
    pass
