# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from


@python_2_unicode_compatible
class Invoice(object):
    """This represents an invoice in the Holvi system"""
    def __init__(self, connection, jsondata=None):
        self.connection = connection
        if not jsondata:
            self._init_empty()
        else:
            self._jsondata = jsondata

    def __getattr__(self, attr):
        if attr[0] != '_':
            return self._jsondata[attr]
        try:
            return object.__getattribute__(self, attr)
        except KeyError as e:
            raise_from(AttributeError, e)

    def _init_empty(self):
        """Creates the base set of attributes invoice has/needs"""
        raise NotImplementedError()

    def send(self, send_email=True):
        """Marks the invoice as sent in Holvi

        If send_email is False then the invoice is *not* automatically emailed to the recipient
        and your must take care of sending the invoice yourself.
        """
        url = str(self.connection.base_url_fmt + 'pool/{pool}/invoice/{code}/status/').format(pool=self.connection.pool, code=self.code)
        payload = {
            'mark_as_sent': True,
            'send_email': send_email,
            'active': True, # It must be active to be sent...
        }
        stat = self.connection.make_put(url, payload)
        #print("Got stat=%s" % stat)
        # TODO: Check the stat and raise error if daft is not false or active is not true ?

    def save(self):
        """Creates or updates the invoice"""
        raise NotImplementedError()


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
            ret.append(Invoice(self.connection, ijson))
        return ret

    def create_invoice(self, invoice):
        """Takes an Invoice and creates it to Holvi"""
        raise NotImplementedError()

    def get_invoice(self, invoice_code):
        """Retvieve given Invoice"""
        url = self.base_url + '{code}/'.format(code=invoice_code)
        ijson = self.connection.make_get(url)
        #print("Got ijson=%s" % ijson)
        return Invoice(self.connection, ijson)
