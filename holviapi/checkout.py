# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
from .utils import HolviObject


@python_2_unicode_compatible
class Order(HolviObject):
    """This represents a checkout in the Holvi system"""
    def __init__(self, api, jsondata=None):
        super(Order, self).__init__(api, jsondata)
        # TODO: parse the product lines to list of OrderProduct objects


@python_2_unicode_compatible
class CheckoutAPI(object):
    """Handles the operations on orders, instantiate with a Connection object"""
    base_url_fmt = 'checkout/v2/'

    def __init__(self, connection):
        self.connection = connection
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt)

    def list_orders(self):
        """Lists all orders in the system"""
        url = self.base_url + 'pool/{pool}/order/'.format(pool=self.connection.pool)
        # TODO add filtering support
        orders = self.connection.make_get(url)
        #print("Got orders=%s" % orders)
        # TODO: Make generator to handle the paging
        ret = []
        for ojson in orders['results']:
            ret.append(Order(self, ojson))
        return ret

    def get_order(self, order_code):
        """Retvieve given Order"""
        url = self.base_url + 'order/{code}'.format(code=order_code)
        ojson = self.connection.make_get(url)
        #print("Got ojson=%s" % ojson)
        return Order(self.connection, ojson)
