import os

import holviapi
import pytest


@pytest.fixture
def connection():
    pool = os.environ.get('HOLVI_POOL', None)
    key = os.environ.get('HOLVI_KEY', None)
    if not pool or not key:
        raise RuntimeError("HOLVI_POOL and HOLVI_KEY must be in ENV for these tests")
    cnc = holviapi.Connection.singleton(pool, key)
    return cnc


@pytest.fixture
def invoicesapi(connection):
    ia = holviapi.InvoiceAPI(connection)
    return ia


@pytest.fixture
def categoriesapi(connection):
    ca = holviapi.CategoriesAPI(connection)
    return ca


@pytest.fixture
def productsapi(connection):
    pa = holviapi.ProductsAPI(connection)
    return pa
