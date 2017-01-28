# -*- coding: utf-8 -*-
import os
import pytest
import holviapi

@pytest.fixture
def connection():
    pool = os.environ.get('HOLVI_POOL', None)
    key = os.environ.get('HOLVI_KEY', None)
    if not pool or not key:
        raise RuntimeError("HOLVI_POOL and HOLVI_KEY must be in ENV for these tests")
    cnc = holviapi.Connection(pool,key)
    return cnc

@pytest.fixture
def invoiceapi():
    cnc = connection()
    ia = holviapi.InvoiceAPI(cnc)
    return ia

@pytest.fixture
def categoriesapi():
    cnc = connection()
    ca = holviapi.CategoriesAPI(cnc)
    return ca

def test_list_invoices(invoiceapi):
    l = invoiceapi.list_invoices()
    i = next(l)
    assert type(i) == holviapi.Invoice

def test_get_invoice(invoiceapi):
    l = invoiceapi.list_invoices()
    i = next(l)
    assert type(i) == holviapi.Invoice
    i2 = invoiceapi.get_invoice(i.code)
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
