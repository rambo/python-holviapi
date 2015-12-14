# -*- coding: utf-8 -*-
import six
from future.utils import python_2_unicode_compatible, raise_from

@python_2_unicode_compatible
class JSONObject(object):
    """Baseclass for objects which have JSON based backend data but also mixed local properties"""
    _jsondata = {}

    def __init__(self, **kwargs):
        self._jsondata.update(kwargs)

    def __getattr__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError as e:
            try:
                return self._jsondata[attr]
            except KeyError as e:
                raise_from(AttributeError(six.u(e)), e)

    def __setattr__(self, attr, val):
        try:
            object.__getattribute__(self, attr)
            object.__setattr__(self, attr, val)
        except AttributeError as e:
            try:
                self._jsondata[attr] = val
            except KeyError as e:
                raise_from(AttributeError(six.u(e)), e)

class HolviObject(JSONObject):
    connection = None

