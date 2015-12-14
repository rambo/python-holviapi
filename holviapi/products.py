# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
from .utils import HolviObject


@python_2_unicode_compatible
class Product(HolviObject):
    """This represents a product in the Holvi system"""


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
