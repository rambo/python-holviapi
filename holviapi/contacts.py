# -*- coding: utf-8 -*-
from __future__ import print_function
import six
from future.utils import python_2_unicode_compatible, raise_from
from .utils import JSONObject


class InvoiceContact(JSONObject): # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for invoice receivers"""
    _valid_keys = ("city", "name", "country", "street", "postcode", "email") # Same for both create and update

    def to_holvi_dict(self):
        return { k:v for (k,v) in self._jsondata.items() if k in self._valid_keys }
