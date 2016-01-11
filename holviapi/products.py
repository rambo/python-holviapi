# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
from .categories import IncomeCategory, CategoriesAPI
from .utils import HolviObject, JSONObject


@python_2_unicode_compatible
class Product(HolviObject):
    """This represents a product in the Holvi system"""
    api = None
    category = None
    questions = []
    _cklass = IncomeCategory
    _valid_keys = ["code", "name", "description", "questions"]  # Not really, there is no API for managing products ATM

    def __init__(self, api, jsondata=None, cklass=None, **kwargs):
        if cklass:
            self._cklass = cklass
        self._fetch_method = api.get_product
        super(Product, self).__init__(api, jsondata, **kwargs)

    def _map_holvi_json_properties(self):
        if self._jsondata.get("category"):
            self.category = self._cklass(self.api.categories_api, {"code": self._jsondata["category"]})
        self.questions = []
        # If we're lazy-loaded we don't have this array
        for qdata in self._jsondata.get("questions", []):
            self.questions.append(ProductQuestion(self, qdata))

    def to_holvi_dict(self, patch=False):
        if self.category:
            self._jsondata["category"] = self.category.code
        self._jsondata["questions"] = []
        for question in self.questions:
            self._jsondata["questions"].append(question.to_holvi_dict())
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered


class ShopProduct(Product):
    """Product from the open budget api, has slightly different angle to things"""
    pass


class OrderProduct(Product):
    """Product from from a checkout"""
    pass


class ProductQuestion(JSONObject):  # We extend JSONObject instead of HolviObject since there is no direct way to manipulate these
    product = None
    _pklass = OrderProduct
    _valid_keys = ("Active", "product", "label", "code", "helptext")

    def __init__(self, product, holvi_dict={}, pklass=None):
        self.product = product
        self.api = self.product.api
        if pklass:
            self._pklass = pklass
        super(ProductQuestion, self).__init__(**holvi_dict)
        self._map_holvi_json_properties()

    def _map_holvi_json_properties(self):
        if self._jsondata.get("product"):
            self.product = self._pklass(self.api, {"code": self._jsondata["product"]})

    def to_holvi_dict(self):
        if self.product:
            self._jsondata["product"] = self.product.code
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered


@python_2_unicode_compatible
class ProductsAPI(object):
    """Handles the operations on products, instantiate with a Connection object"""
    # Currently only read-only access via the open budget api
    base_url_fmt = 'pool/{pool}/openbudget/'

    def __init__(self, connection):
        self.connection = connection
        self.categories_api = CategoriesAPI(self.connection)
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt).format(pool=connection.pool)

    def list_products(self):
        """Lists all products in the system"""
        url = self.base_url
        # TODO add filtering support
        obdata = self.connection.make_get(url)
        #print("Got obdata=%s" % obdata)
        ret = []
        for pjson in obdata['products']:
            ret.append(ShopProduct(self, pjson))
        return ret

    def get_product(self, code):
        """Gets category with given code

        NOTE: Filters the list of income and expense categories in this end due to
        API limitations"""
        candidates = filter(lambda c: c.code == code, self.list_products())
        if not candidates:
            return None
        return next(candidates)
