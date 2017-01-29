# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools as it
from decimal import Decimal

import six
from future.builtins import next, object
from future.utils import python_2_unicode_compatible, raise_from

try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator


ISO_REFERENCE_VALID_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ISO_REFERENCE_VALID_NUMERIC = '0123456789'
ISO_REFERENCE_VALID = ISO_REFERENCE_VALID_NUMERIC + ISO_REFERENCE_VALID_ALPHA


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
                if six.PY2:
                    raise_from(AttributeError(e.message), e)
                else:
                    raise_from(AttributeError(e), e)

    def __setattr__(self, attr, val):
        try:
            object.__getattribute__(self, attr)
            object.__setattr__(self, attr, val)
        except AttributeError as e:
            try:
                self._jsondata[attr] = val
            except KeyError as e:
                if six.PY2:
                    raise_from(AttributeError(e.message), e)
                else:
                    raise_from(AttributeError(e), e)


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


class HolviObjectList(Iterator):
    _klass = None

    def __init__(self, jsondata, api):
        self.api = api
        self.jsondata = jsondata
        self._get_iter()
        self._get_size()

    def _get_iter(self):
        """Must set self._iter"""
        raise NotImplementedError()

    def _get_size(self):
        """Must set self.size"""
        raise NotImplementedError()

    def next(self):
        return self.__next__()

    def __next__(self):
        while True:
            try:
                return self._klass(self.api, next(self._iter))
            except StopIteration:
                next_url = self.jsondata.get("next", False)
                if not next_url:
                    raise
                self.jsondata = self.api.connection.make_get(next_url)
                self._get_iter()
        raise StopIteration

    def __len__(self):
        return self.size


def int2fin_reference(n):
    """Calculates a checksum for a Finnish national reference number"""
    checksum = 10 - (sum([int(c) * i for c, i in zip(str(n)[::-1], it.cycle((7, 3, 1)))]) % 10)
    if checksum == 10:
        checksum = 0
    return "%s%s" % (n, checksum)


def fin_reference_isvalid(n):
    """Check that the given Finnish national reference number is valid (ie the checksum is valid)"""
    return int2fin_reference(str(n)[:-1]) == str(n)


def iso_reference_valid_char(c, raise_error=True):
    """Helper to make sure the given character is valid for a reference number"""
    if c in ISO_REFERENCE_VALID:
        return True
    if raise_error:
        raise ValueError("'%s' is not in '%s'" % (c, ISO_REFERENCE_VALID))
    return False


def iso_reference_char2int(c):
    """Maps the characters in ISO reference (ones starting with RF) to their corresponding integers"""
    iso_reference_valid_char(c, True)
    return (ord(c) - 55)  # A = 10, Z=35


def iso_reference_str2int(n):
    """Creates the huge number from ISO alphanumeric ISO reference"""
    n = n.upper()
    numbers = []
    for c in n:
        iso_reference_valid_char(c)
        if c in ISO_REFERENCE_VALID_NUMERIC:
            numbers.append(c)
        else:
            numbers.append(str(iso_reference_char2int(c)))
    return int(''.join(numbers))


def int2iso_reference(n):
    """Calculates checksum (and adds the RF prefix) for an international reference number from an integer"""
    import warnings
    warnings.warn("Use str2iso_reference instead", DeprecationWarning)
    return str2iso_reference(str(n))


def str2iso_reference(n):
    """Calculates checksum (and adds the RF prefix) for an international reference number from a string (can contain any characters valid for the reference)"""
    cs_source = n + 'RF00'
    cs = 98 - (iso_reference_str2int(cs_source) % 97)
    return "RF%02d%s" % (cs, n)


def iso_reference_isvalid(ref):
    """Validates ISO reference number"""
    ref = str(ref)
    cs_source = ref[4:] + ref[:4]
    return (iso_reference_str2int(cs_source) % 97) == 1


class BarcodeException(Exception):
    pass


def barcode(iban, reference, amount, due=None):
    """Calculates virtual barcode for IBAN account number and ISO reference

    Arguments:
        iban {string} -- IBAN formed account number
        reference {string} -- ISO 11649 creditor reference
        amount {decimal.Decimal} -- Amount in euros, 0.01 - 999999.99
        due {datetime.date} -- due date
    """

    iban = iban.replace(' ', '')
    reference = reference.replace(' ', '')

    if reference.startswith('RF'):
        version = 5
    else:
        version = 4

    if version == 5:
        reference = reference[2:]  # test RF and add 00 where needed
        if len(reference) < 23:
            reference = reference[:2] + ("0" * (23 - len(reference))) + reference[2:]
    elif version == 4:
        reference = reference.zfill(20)

    if not iban.startswith('FI'):
        raise BarcodeException('Barcodes can be printed only for IBANs starting with FI')

    iban = iban[2:]
    amount = "%08d" % (amount.quantize(Decimal('.01')).shift(2).to_integral_value())
    if len(amount) != 8:
        raise BarcodeException("Barcode payment amount must be less than 1000000.00")

    if due:
        due = due.strftime("%y%m%d")
    else:
        due = "000000"

    if version == 4:
        barcode = "%s%s%s000%s%s" % (version, iban, amount, reference, due)
    elif version == 5:
        barcode = "%s%s%s%s%s" % (version, iban, amount, reference, due)

    return barcode
