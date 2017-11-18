# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
from decimal import Decimal

import six
from future.builtins import next, object
from future.utils import python_2_unicode_compatible, raise_from

from .categories import CategoriesAPI, IncomeCategory
from .contacts import InvoiceContact
from .utils import HolviObject, HolviObjectList, JSONObject


class Invoice(HolviObject):
    """This represents an invoice in the Holvi system"""
    items = []
    issue_date = None
    due_date = None
    receiver = None
    _valid_keys = ("currency", "issue_date", "due_date", "items", "receiver", "type", "number", "subject")  # Same for both create and update
    _patch_valid_keys = ("due_date", "issue_date", "subject", "number", "receiver", "items")  # For sent

    def _map_holvi_json_properties(self):
        self.items = []
        for item in self._jsondata["items"]:
            self.items.append(InvoiceItem(self, holvi_dict=item))
        self.issue_date = datetime.datetime.strptime(self._jsondata["issue_date"], "%Y-%m-%d").date()
        self.due_date = datetime.datetime.strptime(self._jsondata["due_date"], "%Y-%m-%d").date()
        self.receiver = InvoiceContact(self._jsondata["receiver"])

    def _init_empty(self):
        """Creates the base set of attributes invoice has/needs"""
        self._jsondata = {
            "code": None,
            "currency": "EUR",
            "subject": "",
            "due_date": (datetime.datetime.now().date() + datetime.timedelta(days=14)).isoformat(),
            "issue_date": datetime.datetime.now().date().isoformat(),
            "number": None,
            "type": "outbound",
            "receiver": {
                "name": "",
                "email": "",
                "street": "",
                "city": "",
                "postcode": "",
                "country": ""
            },
            "items": [],
        }

    def send(self, send_email=True):
        """Marks the invoice as sent in Holvi

        If send_email is False then the invoice is *not* automatically emailed to the recipient
        and your must take care of sending the invoice yourself.
        """
        url = str(self.api.base_url + '{code}/status/').format(code=self.code)  # six.u messes this up
        payload = {
            'mark_as_sent': True,
            'send_email': send_email,
        }
        stat = self.api.connection.make_put(url, payload)
        #print("Got stat=%s" % stat)
        # TODO: Check the stat and raise error if daft is not false or active is not true ?

    def to_holvi_dict(self):
        """Convert our Python object to JSON acceptable to Holvi API"""
        self._jsondata["items"] = []
        for item in self.items:
            self._jsondata["items"].append(item.to_holvi_dict())
        self._jsondata["issue_date"] = self.issue_date.isoformat()
        self._jsondata["due_date"] = self.due_date.isoformat()
        self._jsondata["receiver"] = self.receiver.to_holvi_dict()
        return {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}

    def save(self):
        """Saves this invoice to Holvi, returns the created/updated invoice"""
        if not self.items:
            raise HolviError("No items")
        if not self.subject:
            raise HolviError("No subject")
        send_json = self.to_holvi_dict()
        if self.code:
            url = str(self.api.base_url + '{code}/').format(code=self.code)
            if not self.code:
                send_patch = {k: v for (k, v) in send_json.items() if k in self._patch_valid_keys}
                send_patch["items"] = []
                for item in self.items:
                    send_patch["items"].append(item.to_holvi_dict(True))
                stat = self.api.connection.make_patch(url, send_patch)
            else:
                stat = self.api.connection.make_put(url, send_json)
            return Invoice(self.api, stat)
        else:
            url = str(self.api.base_url)
            stat = self.api.connection.make_post(url, send_json)
            return Invoice(self.api, stat)

    def void(self):
        """Mark invoice as void in Holvi"""
        return self.delete()

    def delete(self):
        """Mark invoice as void in Holvi"""
        url = str(self.api.base_url + '{code}/status/').format(code=self.code)  # six.u messes this up
        payload = {
            'void': True,
        }
        stat = self.api.connection.make_put(url, payload)
        #print("Got stat=%s" % stat)
        # TODO: Check the stat and raise error if active is not what we expected ?


class InvoiceItem(JSONObject):  # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for the items in an Invoice"""
    api = None
    invoice = None
    category = None
    net = None
    gross = None
    _cklass = IncomeCategory
    _valid_keys = ("detailed_price", "category", "description")  # Same for both create and update
    _patch_valid_keys = ("description", "code")

    def __init__(self, invoice, holvi_dict={}, cklass=None):
        self.invoice = invoice
        self.api = self.invoice.api
        if cklass:
            self._cklass = cklass
        super(InvoiceItem, self).__init__(**holvi_dict)
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        if not self._jsondata.get("detailed_price"):
            self._jsondata["detailed_price"] = {"net": "0.00", "gross": "0.00"}
        self.net = Decimal(self._jsondata["detailed_price"].get("net"))
        self.gross = Decimal(self._jsondata["detailed_price"].get("gross"))
        if self._jsondata.get("category"):
            self.category = self._cklass(self.api.categories_api, {"code": self._jsondata["category"]})
        # PONDER: there is a 'product' key in the Holvi JSON for items but it's always None
        #         and the web UI does not allow setting products to invoices

    def to_holvi_dict(self, patch=False):
        if not self.gross:
            self.gross = self.net
        if not self._jsondata.get("detailed_price"):
            self._jsondata["detailed_price"] = {"net": "0.00", "gross": "0.00"}  # "currency" and "vat_rate" are not sent to Holvi
        self._jsondata["detailed_price"]["net"] = self.net.quantize(Decimal(".01")).__str__()  # six.u messes this up
        self._jsondata["detailed_price"]["gross"] = self.gross.quantize(Decimal(".01")).__str__()  # six.u messes this up
        if self.category:
            self._jsondata["category"] = self.category.code
        if patch:
            filter_list = self._patch_valid_keys
        else:
            filter_list = self._valid_keys
        filtered = {k: v for (k, v) in self._jsondata.items() if k in filter_list}
        if "detailed_price" in filtered:
            if "vat_rate" in filtered["detailed_price"]:
                del(filtered["detailed_price"]["vat_rate"])
            if "currency" in filtered["detailed_price"]:
                del(filtered["detailed_price"]["currency"])
        return filtered


class InvoiceList(HolviObjectList):
    _klass = Invoice

    def _get_size(self):
        self.size = len(self.jsondata["list"])

    def _get_iter(self):
        self.jsondata = {"next": None, "list": self.jsondata}
        self._iter = iter(self.jsondata["list"])


@python_2_unicode_compatible
class InvoiceAPI(object):
    """Handles the operations on invoices, instantiate with a Connection object"""
    base_url_fmt = 'pool/{pool}/invoice/'

    def __init__(self, connection):
        self.connection = connection
        self.categories_api = CategoriesAPI(self.connection)
        self.base_url = six.u(connection.base_url_fmt + self.base_url_fmt).format(pool=connection.pool)

    def list_invoices(self, **kwargs):
        """Lists all invoices in the system, returns InvoiceList you can iterate over.

        Add Holvi supported GET filters via kwargs, on 2016.01.13 I was informed following keys are supported:

          - reference (lookup_type='icontains')
          - serial (Slightly complicated: try 'prefix-number-year', 'number-year', 'number', 'prefix')
          - category (exact)
          - receiver (field='receiver.name', lookup_type='icontains')
          - subject (lookup_type='icontains')
          - status (exact)
          - create_time_from (field='create_time', lookup_type='gte')
          - create_time_to (field='create_time', lookup_type='lte')
          - update_time_from (field='update_time', lookup_type='gte')
          - update_time_to (field='update_time', lookup_type='lte')

        All times are ISO datetimes, try for example '2016-01-20T00:00:00.0Z'.

        For other kinds of filtering use Pythons filter() function as usual.
        """
        invoices = self.connection.make_get(self.base_url, params=kwargs)
        return InvoiceList(invoices, self)

    def get_invoice(self, invoice_code):
        """Retvieve given Invoice"""
        url = self.base_url + '{code}/'.format(code=invoice_code)
        ijson = self.connection.make_get(url)
        #print("Got ijson=%s" % ijson)
        return Invoice(self, ijson)
