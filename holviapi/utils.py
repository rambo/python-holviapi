# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools as it

import six
from future.utils import python_2_unicode_compatible, raise_from


@python_2_unicode_compatible
class JSONObject(object):
    """Baseclass for objects which have JSON based backend data but also mixed local properties"""
    _jsondata = {}

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self._jsondata))

    def __init__(self, **kwargs):
        self._jsondata = kwargs

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
    _lazy = False
    _fetch_method = None

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.to_holvi_dict()))

    def __init__(self, api, jsondata=None):
        # We are not calling super() on purpose
        self.api = api
        if not jsondata:
            self._init_empty()
        else:
            if (len(jsondata) == 1
                    and jsondata.get('code')):
                self._lazy = True
            self._jsondata = jsondata
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        """For mapping properties from _jsondata to something more Pythonic

        For really simple objects there is no need to implement this"""
        pass

    def to_holvi_dict(self):
        """For mapping the object back to JSON dict that holvi accepts"""
        return self._jsondata

    def __getattr__(self, attr):
        if object.__getattribute__(self, '_lazy'):
            #print("We're lazy instance!")
            if attr == 'code':  # Do not fetch full object if we're just getting the code
                return object.__getattribute__(self, '_jsondata')['code']
            f = object.__getattribute__(self, '_fetch_method')
            if f is not None:
                #print("Trying to fetch full one with %s" % f)
                new = f(object.__getattribute__(self, '_jsondata')['code'])
                self._jsondata = new._jsondata
                self._map_holvi_json_properties()
                self._lazy = False
            else:
                #print("No fetch method, giving up")
                pass
        return super(HolviObject, self).__getattr__(attr)

    def _init_empty(self):
        """Creates the base set of attributes object has/needs"""
        raise NotImplementedError()

    def save(self):
        """Creates or updates the object"""
        raise NotImplementedError()


def int2fin_reference(n):
    """Calculates a checksum for a Finnish national reference number"""
    checksum = 10 - (sum([int(c) * i for c, i in zip(str(n)[::-1], it.cycle((7, 3, 1)))]) % 10)
    return "%s%s" % (n, checksum)


def fin_reference_isvalid(n):
    """Check that the given Finnish national reference number is valid (ie the checksum is valid)"""
    return int2fin_reference(str(n)[:-1]) == str(n)


def int2iso_reference(n):
    """Calculates checksum (and adds the RF prefix) for an international reference number"""
    n = int(n)
    nt = n * 1000000 + 271500
    checksum = 98 - (nt % 97)
    return "RF%02d%d" % (checksum, n)

# TODO: Add function to check that the iso reference is valid
