# -*- coding: utf-8 -*-
from __future__ import print_function

import six
from future.builtins import next, object
from future.utils import python_2_unicode_compatible, raise_from

from .utils import JSONObject


class InvoiceContact(JSONObject):  # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for invoice receivers"""
    _valid_keys = ("city", "name", "country", "street", "postcode", "email")  # Same for both create and update

    def __init__(self, jsondata=None):
        self._init_empty()
        self._jsondata.update(jsondata)
        # Not calling super on purpose

    def _init_empty(self):
        self._jsondata = {
            "city": "",
            "name": "",
            "country": "",
            "email": "",
            "postcode": "",
            "street": "",
        }

    def to_holvi_dict(self):
        return {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}


class OrderContact(JSONObject):  # aka buyer
    """Pythonic wrapper for order contact info, aka buyer"""
    _valid_keys = ("postcode", "country", "lastname", "country_code", "street", "email", "company", "firstname", "city", "eu_vat_identifier")

    def __init__(self, jsondata=None):
        self._init_empty()
        self._jsondata.update(jsondata)
        # Not calling super on purpose

    def _init_empty(self):
        self._jsondata = {
            "city": "",
            "company": "",
            "country": "",
            "country_code": "",
            "email": "",
            "firstname": "",
            "lastname": "",
            "postcode": "",
            "street": "",
            "eu_vat_identifier": "",
        }

    def to_holvi_dict(self, patch=False):
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered
