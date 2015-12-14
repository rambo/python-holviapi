# -*- coding: utf-8 -*-
import six
from future.utils import python_2_unicode_compatible, raise_from
import itertools as it

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
    """Holvi objects are JSONObject with reference to the relevant API instance"""
    api = None

    def __init__(self, api, jsondata=None):
        # We are not calling super() on purpose
        self.api = api
        if not jsondata:
            self._init_empty()
        else:
            self._jsondata = jsondata

    def _init_empty(self):
        """Creates the base set of attributes object has/needs"""
        raise NotImplementedError()

    def save(self):
        """Creates or updates the object"""
        raise NotImplementedError()
