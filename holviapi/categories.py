# -*- coding: utf-8 -*-
from __future__ import print_function
from future.utils import python_2_unicode_compatible, raise_from
from .utils import HolviObject


@python_2_unicode_compatible
class Category(HolviObject):
    """Baseclass for income/expense categories, do not instantiate directly"""
    def __init__(self, connection, jsondata=None):
        self.connection = connection
        if not jsondata:
            self._init_empty()
        else:
            self._jsondata = jsondata

    def _init_empty(self):
        """Creates the base set of attributes category has/needs"""
        raise NotImplementedError()

    def save(self):
        """Creates or updates the category"""
        raise NotImplementedError()


class IncomeCategory(Category):
    """This represents an income category in the Holvi system"""
    pass


class ExpenseCategory(Category):
    """This represents an expense category in the Holvi system"""
    pass


@python_2_unicode_compatible
class CategoriesAPI(object):
    """Handles the operations on income/expense categories, instantiate with a Connection object"""
    # Currently only read-only access via the open budget api
    base_url_fmt = 'pool/{pool}/openbudget/'

    def __init__(self, connection):
        self.connection = connection
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt).format(pool=connection.pool)

    def list_income_categories(self):
        """Lists all income categories in the system"""
        url = self.base_url
        obdata = self.connection.make_get(url)
        #print("Got obdata=%s" % obdata)
        ret = []
        for icjson in obdata['income_categories']:
            ret.append(IncomeCategory(self.connection, icjson))
        return ret

    def list_expense_categories(self):
        """Lists all expense categories in the system"""
        url = self.base_url
        obdata = self.connection.make_get(url)
        #print("Got obdata=%s" % obdata)
        ret = []
        for ecjson in obdata['expense_categories']:
            ret.append(ExpenseCategory(self.connection, ecjson))
        return ret
