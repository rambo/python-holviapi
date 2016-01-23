# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime
from decimal import Decimal

import dateutil.parser
import six
from future.builtins import next, object
from future.utils import python_2_unicode_compatible, raise_from

from .categories import CategoriesAPI, IncomeCategory
from .contacts import OrderContact
from .products import OrderProduct, ProductQuestion, ProductsAPI
from .utils import HolviObject, HolviObjectList, JSONObject


class Order(HolviObject):
    """This represents a checkout in the Holvi system"""
    buyer = None
    purchases = []
    _valid_keys = ("city", "lastname", "discount_code", "failure_url", "eu_vat_identifier", "postcode", "firstname", "notification_url", "country", "street", "pool", "cancel_url", "company", "success_url", "purchases", "email")
    create_time = None
    update_time = None
    processed_time = None
    paid_time = None

    def _map_holvi_json_properties(self):
        self.buyer = OrderContact({k: v for (k, v) in self._jsondata.items() if k in OrderContact._valid_keys})
        self.purchases = []
        for pdata in self._jsondata["purchases"]:
            self.purchases.append(CheckoutItem(self, pdata))
        for prop in ("create_time", "update_time", "processed_time", "paid_time"):
            if prop not in self._jsondata:
                continue
            if not self._jsondata[prop]:
                continue
            setattr(self, prop, dateutil.parser.parse(self._jsondata[prop]))

    def to_holvi_dict(self):
        if self.buyer:
            self._jsondata.update(self.buyer.to_holvi_dict())
        self._jsondata["purchases"] = []
        for purchase in self.purchases:
            self._jsondata["purchases"].append(purchase.to_holvi_dict())
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered

    def _init_empty(self):
        """Creates the base set of attributes order has/needs"""
        self._jsondata = {
            "code": None,
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
        return sum((x.net for x in self.purchases))

    @property
    def gross(self):
        return sum((x.gross for x in self.purchases))

    def save(self):
        """Saves this order to Holvi, returns a tuple with the order itself and checkout_uri"""
        if self.code:
            raise HolviError("Orders cannot be updated")
        send_json = self.to_holvi_dict()
        send_json.update({
            'pool': self.api.connection.pool
        })
        url = six.u(self.api.base_url + "order/")
        stat = self.api.connection.make_post(url, send_json)
        code = stat["details_uri"].split("/")[-2]  # Maybe slightly ugly but I don't want to basically reimplement all but uri formation of the api method
        return (stat["checkout_uri"], self.api.get_order(code))


class CheckoutItem(JSONObject):  # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for the items/purchaces in an Order"""
    api = None
    order = None
    product = None
    net = None
    gross = None
    _pklass = OrderProduct
    _valid_keys = ("product", "answers", "detailed_price")
    create_time = None
    update_time = None
    answers = []

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
        if "detailed_price" in self._jsondata:
            self.net = Decimal(self._jsondata["detailed_price"].get("net"))
            self.gross = Decimal(self._jsondata["detailed_price"].get("gross"))
        for prop in ("create_time", "update_time"):
            if prop not in self._jsondata:
                continue
            if not self._jsondata[prop]:
                continue
            setattr(self, prop, dateutil.parser.parse(self._jsondata[prop]))
        self.answers = []
        for adata in self._jsondata.get("answers", []):
            self.answers.append(CheckoutItemAnswer(self, adata))

    def to_holvi_dict(self):
        if self.answers:
            self._jsondata["answers"] = []
            for answer in self.answers:
                self._jsondata["answers"].append(answer.to_holvi_dict())
        elif "answers" in self._jsondata:
            del(self._jsondata["answers"])
        # If detailed price is not set then product price will be used
        if self.net is not None:
            if not self.gross:
                self.gross = self.net
            if not self._jsondata.get("detailed_price"):
                self._jsondata["detailed_price"] = {"net": "0.00", "gross": "0.00", "vat_rate": None}  # We need to make sure these exist for the mapping below
            self._jsondata["detailed_price"]["net"] = self.net.quantize(Decimal(".01")).__str__()  # six.u messes this up
            self._jsondata["detailed_price"]["gross"] = self.gross.quantize(Decimal(".01")).__str__()  # six.u messes this up
        if self.product:
            self._jsondata["product"] = self.product.code
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered


class CheckoutItemAnswer(JSONObject):  # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    """Pythonic wrapper for the answers to product questions"""
    api = None
    item = None
    question = None
    _valid_keys = ("question", "label", "answer")
    _qklass = ProductQuestion

    def __init__(self, item, holvi_dict={}, qklass=None):
        self.item = item
        self.api = self.item.api
        if qklass:
            self._qklass = qklass
        super(CheckoutItemAnswer, self).__init__(**holvi_dict)
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        if self._jsondata.get("question"):
            self.question = self._qklass(self.item.product, {"code": self._jsondata["question"]})

    def to_holvi_dict(self):
        if "label" not in self._jsondata:
            self._jsondata["label"] = ""
        if self.question:
            self._jsondata["question"] = self.question.code
            if not self._jsondata["label"]:
                self._jsondata["label"] = self.question.label
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered


class OrderList(HolviObjectList):
    _klass = Order

    def _get_size(self):
        self.size = self.jsondata["count"]

    def _get_iter(self):
        self._iter = iter(self.jsondata["results"])


@python_2_unicode_compatible
class CheckoutAPI(object):
    """Handles the operations on orders, instantiate with a Connection object"""
    base_url_fmt = "checkout/v2/"

    def __init__(self, connection):
        self.connection = connection
        self.categories_api = CategoriesAPI(self.connection)
        self.products_api = ProductsAPI(self.connection)
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt)

    def list_orders(self, **kwargs):
        """Lists all orders in the system, returns OrderList you can iterate over.

        Add Holvi supported GET filters via kwargs, API documentation (last update time unknown) says following keys are supported:

          - filter_paid_time_from (datetime): Returns orders that are paid on or after the given datetime.
          - filter_paid_time_to (datetime): Returns orders that are paid on or before the given datetime.
          - filter_update_time_from (datetime): Returns orders that are updated on or after the given datetime.
          - filter_update_time_to (datetime): Returns orders that are updated on or before the given datetime.
          - firstname (string): Returns orders where buyer's first name matches the given string (parial, case insensitive match)
          - lastname (string): Returns orders where buyer's last name matches the given string (parial, case insensitive match)
          - street (string): Returns orders where buyer's street address matches the given string (parial, case insensitive match)
          - city (string): Returns orders where buyer's city matches the given string (parial, case insensitive match)
          - postcode (string): Returns orders where buyer's postcode matches the given string (parial, case insensitive match)
          - country (string): Returns orders where buyer's country matches the given string (parial, case insensitive match)
          - email (string): Returns orders where buyer's email address matches the given string (parial, case insensitive match)
          - company (string): Returns orders where buyer's company name matches the given string (parial, case insensitive match)

        All times are ISO datetimes, try for example '2016-01-20T00:00:00.0Z'.

        For other kinds of filtering use Pythons filter() function as usual.
        """
        url = self.base_url + "pool/{pool}/order/".format(pool=self.connection.pool)
        orders = self.connection.make_get(url, params=kwargs)
        return OrderList(orders, self)

    def get_order(self, order_code):
        """Retvieve given Order"""
        url = self.base_url + "order/{code}".format(code=order_code)
        ojson = self.connection.make_get(url)
        #print("Got ojson=%s" % ojson)
        return Order(self, ojson)
