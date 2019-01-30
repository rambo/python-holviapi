# -*- coding: utf-8 -*-
import os

import holviapi
import pytest

from .fixtures import categoriesapi, connection, invoicesapi, productsapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_KEY')), reason="HOLVI_POOL and HOLVI_KEY must be in ENV for these tests")


def test_list_invoices(invoicesapi):
    l = invoicesapi.list_invoices()
    i = next(l)
    assert type(i) == holviapi.Invoice


def test_get_invoice(invoicesapi):
    l = invoicesapi.list_invoices()
    i = next(l)
    assert type(i) == holviapi.Invoice
    i2 = invoicesapi.get_invoice(i.code)
    assert i.code == i2.code


def test_list_income_categories(categoriesapi):
    l = categoriesapi.list_income_categories()
    c = next(l)
    assert type(c) == holviapi.IncomeCategory


def test_list_expense_categories(categoriesapi):
    l = categoriesapi.list_expense_categories()
    c = next(l)
    assert type(c) == holviapi.ExpenseCategory


def test_get_category(categoriesapi):
    l = categoriesapi.list_income_categories()
    c = next(l)
    assert type(c) == holviapi.IncomeCategory
    c2 = categoriesapi.get_category(c.code)
    assert c.code == c2.code


def test_list_products(productsapi):
    l = productsapi.list_products()
    p = next(l)
    assert type(p) == holviapi.ShopProduct


def test_get_product(productsapi):
    l = productsapi.list_products()
    p = next(l)
    assert type(p) == holviapi.ShopProduct
    p2 = productsapi.get_product(p.code)
    assert p.code == p2.code
