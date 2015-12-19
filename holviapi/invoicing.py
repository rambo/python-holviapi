# -*- coding: utf-8 -*-
from __future__ import print_function
import six
from future.utils import python_2_unicode_compatible, raise_from
import datetime
from decimal import Decimal
from .utils import HolviObject, JSONObject
from .categories import IncomeCategory, CategoriesAPI

class Invoice(HolviObject):
    """This represents an invoice in the Holvi system"""
    items = []
    issue_date = None
    due_date = None

    def _map_holvi_json_properties(self):
        self.items = []
        for item in self._jsondata["items"]:
            self.items.append(InvoiceItem(self, holvi_dict=item))
        self.issue_date = datetime.datetime.strptime(self._jsondata["issue_date"], "%Y-%m-%d").date()
        self.due_date = datetime.datetime.strptime(self._jsondata["due_date"], "%Y-%m-%d").date()

    def _init_empty(self):
        """Creates the base set of attributes invoice has/needs"""
        self._jsondata = {
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
        url = str(self.api.base_url + '{code}/status/').format(code=self.code)
        payload = {
            'mark_as_sent': True,
            'send_email': send_email,
            'active': True, # It must be active to be sent...
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
        return self._jsondata


class InvoiceItem(JSONObject): # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for the items in an Invoice"""
    api = None
    invoice = None
    category = None
    net = None
    gross = None
    _cklass = IncomeCategory

    def __init__(self, invoice, holvi_dict={}, cklass=None):
        self.invoice = invoice
        self.api = self.invoice.api
        if cklass:
            self._cklass = cklass
        super(InvoiceItem, self).__init__(**holvi_dict)
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        self.net = Decimal(self._jsondata["detailed_price"]["net"])
        self.gross = Decimal(self._jsondata["detailed_price"]["gross"])
        if self._jsondata.get("category"):
            self.category = self._cklass(self.api.categories_api, {"code": self._jsondata["category"]})
        # PONDER: there is a 'product' key in the Holvi JSON for items but it's always None
        #         and the web UI does not allow setting products to invoices

    def to_holvi_dict(self):
        if not self.gross:
            self.gross = self.net
        if not self._jsondata.get("detailed_price"):
            self._jsondata["detailed_price"] = { 'net': '0.00', 'gross': '0.00', 'currency': 'EUR', 'vat_rate': None }
        self._jsondata["detailed_price"]["net"] = six.u(self.net.quantize(Decimal('.01')))
        self._jsondata["detailed_price"]["gross"] = six.u(self.net.quantize(Decimal('.01')))
        if self.category:
            self._jsondata["category"] = self.category.code
        return self._jsondata


@python_2_unicode_compatible
class InvoiceAPI(object):
    """Handles the operations on invoices, instantiate with a Connection object"""
    base_url_fmt = 'pool/{pool}/invoice/'

    def __init__(self, connection):
        self.connection = connection
        self.categories_api = CategoriesAPI(self.connection)
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt).format(pool=connection.pool)

    def list_invoices(self):
        """Lists all invoices in the system"""
        # TODO add filtering support (if/when holvi adds it)
        invoices = self.connection.make_get(self.base_url)
        #print("Got invoices=%s" % invoices)
        ret = []
        for ijson in invoices:
            ret.append(Invoice(self, ijson))
        return ret

    def create_invoice(self, invoice):
        """Takes an Invoice and creates it to Holvi"""
        raise NotImplementedError()

    def get_invoice(self, invoice_code):
        """Retvieve given Invoice"""
        url = self.base_url + '{code}/'.format(code=invoice_code)
        ijson = self.connection.make_get(url)
        #print("Got ijson=%s" % ijson)
        return Invoice(self, ijson)
