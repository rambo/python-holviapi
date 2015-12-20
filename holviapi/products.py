# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
from .categories import IncomeCategory, CategoriesAPI
from .utils import HolviObject


@python_2_unicode_compatible
class Product(HolviObject):
    """This represents a product in the Holvi system"""
    api = None
    category = None
    _cklass = IncomeCategory
    _valid_keys = ["code", "name", "description"] # Not really, there is no API for managing products ATM

    def __init__(self, api, jsondata=None, cklass=None, **kwargs):
        if cklass:
            self._cklass = cklass
        self._fetch_method = api.get_product
        super(Product, self).__init__(api, jsondata, **kwargs)

    def _map_holvi_json_properties(self):
        if self._jsondata.get("category"):
            self.category = self._cklass(self.api.categories_api, {"code": self._jsondata["category"]})

    def to_holvi_dict(self, patch=False):
        if self.category:
            self._jsondata["category"] = self.category.code
        filtered = { k:v for (k,v) in self._jsondata.items() if k in self._valid_keys }
        return filtered


class ShopProduct(Product):
    """Product from the open budget api, has slightly different angle to things"""
    pass


class OrderProduct(Product):
    """Product from from a checkout"""
    pass


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
