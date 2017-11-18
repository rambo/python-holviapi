# -*- coding: utf-8 -*-
import datetime
import os
from decimal import Decimal

import pytest

import holviapi

from .test_api_idempotent import categoriesapi, invoicesapi, productsapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_KEY') or not bool(os.environ.get('HOLVI_ALLOW_DANGEROUS'))), reason="HOLVI_POOL, HOLVI_KEY and HOLVI_ALLOW_DANGEROUS must be in ENV for these tests")


def test_create_delete_invoice(invoicesapi):
    ni = holviapi.Invoice(invoicesapi)
    ni.receiver.email = os.environ.get('HOLVI_INVOICE_TO', "example@example.com")
    ni.receiver.name = "Example Person"
    ni.items.append(holviapi.InvoiceItem(ni))
    ni.items[0].description = "API-test %s" % datetime.datetime.now().isoformat()
    ni.items[0].net = Decimal("25.50")
    ni.subject = "%s / %s" % (ni.items[0].description, ni.receiver.name)
    resp = ni.save()
    assert resp.code
    resp.delete()


@pytest.mark.skipif(not os.environ.get('HOLVI_INVOICE_TO'), reason="HOLVI_INVOICE_TO must be defined for this test")
def test_create_send_invoice(invoicesapi):
    ni = holviapi.Invoice(invoicesapi)
    ni.receiver.email = os.environ.get('HOLVI_INVOICE_TO')
    ni.receiver.name = "Example Person"
    ni.items.append(holviapi.InvoiceItem(ni))
    ni.items[0].description = "API-test %s" % datetime.datetime.now().isoformat()
    ni.items[0].net = Decimal("25.50")
    ni.subject = "%s / %s" % (ni.items[0].description, ni.receiver.name)
    resp = ni.save()
    assert resp.code
    resp.send()
