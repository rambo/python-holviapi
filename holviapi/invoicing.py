# -*- coding: utf-8 -*-
from __future__ import print_function
import six
from future.utils import python_2_unicode_compatible, raise_from
import datetime
import decimal
from .utils import HolviObject
from .categories import IncomeCategory

@python_2_unicode_compatible
class Invoice(HolviObject):
    """This represents an invoice in the Holvi system"""
    items = []

    def __init__(self, api, jsondata=None):
        super(Invoice, self).__init__(api, jsondata)
        self.items = []
        for item in self._jsondata["items"]:
            self.items.append(InvoiceItem(self, holvi_dict=item))

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
        self._jsondata["items"] = []
        for item in self.items:
            self._jsondata["items"].append(item.to_holvi_dict())
        return self._jsondata


class InvoiceItem(object):
    category = None
    description = None
    net = None
    gross = None
    _cklass = IncomeCategory

    def __init__(self, api, net=None, desc=None, holvi_dict=None, cklass=None):
        if cklass:
            self._cklass = cklass
        self.api = api
        self.net = net
        self.description = desc
        if holvi_dict:
            self.from_holvi_dict(holvi_dict)

    def from_holvi_dict(self, d):
        self.net = decimal.Decimal(d["detailed_price"]["net"])
        self.gross = decimal.Decimal(d["detailed_price"]["gross"])
        self.description = d["description"]
        self.category = self._cklass(self.api, {"code": d["category"]})

    def to_holvi_dict(self):
        if not self.gross:
            self.gross = self.net
        r = {
            "detailed_price": {
              "net": six.u(self.net.quantize(Decimal('.01'))),
              "gross": six.u(self.gross.quantize(Decimal('.01'))),
            },
            "description": self.description,
            "category": "",
        }
        if self.category:
            r["category"] = self.category.code
        return r


@python_2_unicode_compatible
class InvoiceAPI(object):
    """Handles the operations on invoices, instantiate with a Connection object"""
    base_url_fmt = 'pool/{pool}/invoice/'

    def __init__(self, connection):
        self.connection = connection
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
