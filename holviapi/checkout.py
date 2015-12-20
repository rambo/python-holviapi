# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
import datetime
from decimal import Decimal
from .utils import HolviObject, JSONObject
from .products import ProductsAPI, OrderProduct
from .categories import IncomeCategory, CategoriesAPI
from .contacts import OrderContact


class Order(HolviObject):
    """This represents a checkout in the Holvi system"""
    buyer = None
    purchases = []
    _valid_keys = ("city", "lastname", "discount_code", "failure_url", "eu_vat_identifier", "postcode", "firstname", "notification_url", "country", "street", "pool", "cancel_url", "company", "success_url", "purchases", "email")

    def _map_holvi_json_properties(self):
        self.buyer = OrderContact({ k:v for (k,v) in self._jsondata.items() if k in OrderContact._valid_keys })
        self.purchases = []
        for pdata in self._jsondata["purchases"]:
            self.purchases.append(CheckoutItem(self, pdata))
        # TODO: Map the _time properties even though they are not editable

    def to_holvi_dict(self):
        if self.buyer:
            self._jsondata.update(self.buyer.to_holvi_dict())
        self._jsondata["purchases"] = []
        for purchase in self.purchases:
            self._jsondata["purchases"].append(purchase.to_holvi_dict())
        filtered = { k:v for (k,v) in self._jsondata.items() if k in self._valid_keys }
        return filtered

    def _init_empty(self):
        """Creates the base set of attributes order has/needs"""
        self._jsondata = {
            "pool": self.api.connection.pool,
            "purchases": [],
            "discount_code": "",
            "city": "",
            "firstname": "",
            "lastname": "",
            "company": "",
            "eu_vat_identifier": "",
            "street": "",
            "postcode": "",
            "country": "",
            "email": "",
            "cancel_url": "",
            "success_url": "",
            "failure_url": "",
            "notification_url": "",
        }

    @property
    def net(self):
        return sum(( x.net for x in self.purchases ))

    @property
    def gross(self):
        return sum(( x.gross for x in self.purchases ))


class CheckoutItem(JSONObject): # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for the items/purchaes in an Order"""
    api = None
    order = None
    product = None
    net = None
    gross = None
    _pklass = OrderProduct
    _valid_keys = ("product", "answers")

    def __init__(self, order, holvi_dict={}, pklass=None):
        self.order = order
        self.api = self.order.api
        if pklass:
            self._pklass = pklass
        super(CheckoutItem, self).__init__(**holvi_dict)
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        if self._jsondata.get("product"):
            self.product = self._pklass(self.api.products_api, {"code": self._jsondata["product"]})
        if not self._jsondata.get("detailed_price"):
            self._jsondata["detailed_price"] = { "net": "0.00", "gross": "0.00" }
        self.net = Decimal(self._jsondata["detailed_price"].get("net"))
        self.gross = Decimal(self._jsondata["detailed_price"].get("gross"))
        # TODO: Map answers
        # TODO: Map the _time properties even though they are not editable

    def to_holvi_dict(self):
        # TODO: Handle answers
        if not self.gross:
            self.gross = self.net
        if not self._jsondata.get("detailed_price"):
            self._jsondata["detailed_price"] = { "net": "0.00", "gross": "0.00" } # These are not actually sent to holvi in the order but we need to make sure they exist for the mapping below
        self._jsondata["detailed_price"]["net"] = self.net.quantize(Decimal(".01")).__str__() # six.u messes this up
        self._jsondata["detailed_price"]["gross"] = self.gross.quantize(Decimal(".01")).__str__() # six.u messes this up
        if self.product:
            self._jsondata["product"] = self.product.code
        filtered = { k:v for (k,v) in self._jsondata.items() if k in self._valid_keys }
        return filtered


@python_2_unicode_compatible
class CheckoutAPI(object):
    """Handles the operations on orders, instantiate with a Connection object"""
    base_url_fmt = "checkout/v2/"

    def __init__(self, connection):
        self.connection = connection
        self.categories_api = CategoriesAPI(self.connection)
        self.products_api = ProductsAPI(self.connection)
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt)

    def list_orders(self):
        """Lists all orders in the system"""
        url = self.base_url + "pool/{pool}/order/".format(pool=self.connection.pool)
        # TODO add filtering support
        orders = self.connection.make_get(url)
        #print("Got orders=%s" % orders)
        # TODO: Make generator to handle the paging
        ret = []
        for ojson in orders["results"]:
            ret.append(Order(self, ojson))
        return ret

    def get_order(self, order_code):
        """Retvieve given Order"""
        url = self.base_url + "order/{code}".format(code=order_code)
        ojson = self.connection.make_get(url)
        #print("Got ojson=%s" % ojson)
        return Order(self, ojson)
