# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools

from future.builtins import next, object
from future.builtins.iterators import filter
from future.utils import python_2_unicode_compatible, raise_from

from .utils import HolviObject, HolviObjectList, JSONObject


class Category(HolviObject):
    """Baseclass for income/expense categories, do not instantiate directly"""

    def __init__(self, api, jsondata=None, **kwargs):
        self._fetch_method = api.get_category
        super(Category, self).__init__(api, jsondata, **kwargs)


class IncomeCategory(Category):
    """This represents an income category in the Holvi system"""
    pass


class ExpenseCategory(Category):
    """This represents an expense category in the Holvi system"""
    pass


class CategoryList(HolviObjectList):

    def _get_size(self):
        self.size = len(self.jsondata[self._key])

    def _get_iter(self):
        self._iter = iter(self.jsondata[self._key])


class IncomeCategoryList(CategoryList):
    _klass = IncomeCategory
    _key = "income_categories"


class ExpenseCategoryList(CategoryList):
    _klass = ExpenseCategory
    _key = "expense_categories"


@python_2_unicode_compatible
class CategoriesAPI(object):
    """Handles the operations on income/expense categories, instantiate with a Connection object"""
    # Currently only read-only access via the open budget api
    base_url_fmt = 'pool/{pool}/openbudget/'

    def __init__(self, connection):
        self.connection = connection
        self.base_url = str(connection.base_url_fmt + self.base_url_fmt).format(pool=connection.pool)

    def list_income_categories(self):
        """Lists all products in the system, returns IncomeCategoryList you can iterate over.

        Holvi API does not currently support server-side filtering so you will have to use Pythons filter() function as usual.
        """
        url = self.base_url
        obdata = self.connection.make_get(url)
        return IncomeCategoryList(obdata, self)

    def list_expense_categories(self):
        """Lists all products in the system, returns ExpenseCategoryList you can iterate over.

        Holvi API does not currently support server-side filtering so you will have to use Pythons filter() function as usual.
        """
        url = self.base_url
        obdata = self.connection.make_get(url)
        return ExpenseCategoryList(obdata, self)

    def get_category(self, code):
        """Gets category with given code

        NOTE: Filters the list of income and expense categories in this end due to API limitations"""
        candidates = list(filter(lambda c: c.code == code, itertools.chain(self.list_income_categories(), self.list_expense_categories())))
        if not len(candidates):
            return None
        return candidates[0]
