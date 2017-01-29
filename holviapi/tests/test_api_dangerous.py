# -*- coding: utf-8 -*-
import os
import datetime
from decimal import Decimal
import pytest
import holviapi
from .test_api_idempotent import invoicesapi, categoriesapi, productsapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_KEY') or not bool(os.environ.get('HOLVI_ALLOW_DANGEROUS'))), reason="HOLVI_POOL, HOLVI_KEY and HOLVI_ALLOW_DANGEROUS must be in ENV for these tests")

def test_create_delete_invoice(invoicesapi):
    ni = holviapi.Invoice(invoicesapi)
    ni.receiver.email = "example@example.com"
    ni.receiver.name = "Example Person"
    ni.items.append(holviapi.InvoiceItem(ni))
    ni.items[0].description = "API-test %s" % datetime.datetime.now().isoformat()
    ni.items[0].net = Decimal("25.50")
    ni.subject = "%s / %s" % (ni.items[0].description, ni.receiver.name)
    resp = ni.save()
    assert resp.code
    resp.delete()
