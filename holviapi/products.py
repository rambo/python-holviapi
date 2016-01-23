# -*- coding: utf-8 -*-
from __future__ import print_function

from future.builtins import next, object
from future.builtins.iterators import filter
from future.utils import python_2_unicode_compatible, raise_from

from .categories import CategoriesAPI, IncomeCategory
from .utils import HolviObject, HolviObjectList, JSONObject


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

    def get_question(self, code):
        if self._lazy:
            # Trigger full fetch
            self.name
        candidates = filter(lambda c: c.code == code, self.questions)
        if not candidates:
            return None
        return next(candidates)


class ShopProduct(Product):
    """Product from the open budget api, has slightly different angle to things"""
    pass


class OrderProduct(Product):
    """Product from from a checkout"""
    pass


class ProductQuestion(HolviObject):  # We extend HolviObject even though there is no direct way to manipulate these, for lazy-loading support
    product = None
    _pklass = OrderProduct
    _valid_keys = ("active", "product", "label", "code", "helptext")

    def __init__(self, product, holvi_dict={}, pklass=None):
        self.product = product
        if pklass:
            self._pklass = pklass
        self._fetch_method = self.product.get_question
        super(ProductQuestion, self).__init__(self.product.api, holvi_dict)

    def _map_holvi_json_properties(self):
        if self._jsondata.get("product"):
            self.product = self._pklass(self.api, {"code": self._jsondata["product"]})

    def to_holvi_dict(self):
        if self.product:
            self._jsondata["product"] = self.product.code
        filtered = {k: v for (k, v) in self._jsondata.items() if k in self._valid_keys}
        return filtered


class ProductList(HolviObjectList):
    _klass = ShopProduct

    def _get_size(self):
        self.size = len(self.jsondata["products"])

    def _get_iter(self):
        self._iter = iter(self.jsondata["products"])


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
        """Lists all products in the system, returns ProductList you can iterate over.

        Holvi API does not currently support server-side filtering so you will have to use Pythons filter() function as usual.
        """
        url = self.base_url
        # TODO add filtering support when holvi api supports it
        obdata = self.connection.make_get(url)
        return ProductList(obdata, self)

    def get_product(self, code):
        """Gets product with given code

        NOTE: Filters the list of products in this end due to API limitations"""
        candidates = list(filter(lambda c: c.code == code, self.list_products()))
        if not len(candidates):
            return None
        return candidates[0]
