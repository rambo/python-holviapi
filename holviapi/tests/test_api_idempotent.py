# -*- coding: utf-8 -*-
import os

import pytest

import holviapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_KEY')), reason="HOLVI_POOL and HOLVI_KEY must be in ENV for these tests")


@pytest.fixture
def connection():
    pool = os.environ.get('HOLVI_POOL', None)
    key = os.environ.get('HOLVI_KEY', None)
    if not pool or not key:
        raise RuntimeError("HOLVI_POOL and HOLVI_KEY must be in ENV for these tests")
    cnc = holviapi.Connection.singleton(pool, key)
    return cnc


@pytest.fixture
def invoicesapi():
    cnc = connection()
    ia = holviapi.InvoiceAPI(cnc)
    return ia


@pytest.fixture
def categoriesapi():
    cnc = connection()
    ca = holviapi.CategoriesAPI(cnc)
    return ca


@pytest.fixture
def productsapi():
    cnc = connection()
    pa = holviapi.ProductsAPI(cnc)
    return pa


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
