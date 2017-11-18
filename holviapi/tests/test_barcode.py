# -*- coding: utf-8 -*-
import random
from datetime import date
from decimal import Decimal

import pytest

from holviapi.utils import BarcodeException, barcode


def test_barcode_v5():
    """Test valid inputs from specification for v5"""
    assert barcode(iban="FI79 4405 2020 0360 82", reference="RF09 8685 1625 9619 897", amount=Decimal("4883.15"), due=date(2010, 6, 12)) == "579440520200360820048831509000000868516259619897100612"
    assert barcode(iban="FI58 1017 1000 0001 22", reference="RF06 5595 8224 3294 671", amount=Decimal("482.99"), due=date(2010, 1, 31)) == "558101710000001220004829906000000559582243294671100131"
    assert barcode(iban="FI02 5000 4640 0013 02", reference="RF02 6987 5672 0834", amount=Decimal("693.80"), due=date(2011, 7, 24)) == "502500046400013020006938002000000000698756720834110724"
    assert barcode(iban="FI15 6601 0001 5306 41", reference="RF84 7758 4747 9064 7489", amount=Decimal("7444.54"), due=date(2019, 12, 19)) == "515660100015306410074445484000007758474790647489191219"
    assert barcode(iban="FI16 8000 1400 0502 67", reference="RF60 7877 7679 6566 2868 7", amount=Decimal("935.85")) == "516800014000502670009358560000078777679656628687000000"
    assert barcode(iban="FI73 3131 3001 0000 58", reference="RF10 8686 24", amount=Decimal("0.00"), due=date(2013, 8, 9)) == "573313130010000580000000010000000000000000868624130809"
    assert barcode(iban="FI83 3301 0001 1007 75", reference="RF71 9212 5374 2525 3989 7737", amount=Decimal("150000.20"), due=date(2016, 5, 25)) == "583330100011007751500002071092125374252539897737160525"
    assert barcode(iban="FI39 3636 3002 0924 92", reference="RF66 5907 3839 0", amount=Decimal("1.03"), due=date(2023, 3, 11)) == "539363630020924920000010366000000000000590738390230311"
    assert barcode(iban="FI92 3939 0001 0033 91", reference="RF95 1357 914", amount=Decimal("0.02"), due=date(2099, 12, 24)) == "592393900010033910000000295000000000000001357914991224"


def test_barcode_v4():
    """Test valid inputs from specification for v4"""
    assert barcode(iban="FI79 4405 2020 0360 82", reference="86851 62596 19897", amount=Decimal("4883.15"), due=date(2010, 6, 12)) == "479440520200360820048831500000000868516259619897100612"
    assert barcode(iban="FI58 1017 1000 0001 22", reference="55958 22432 94671", amount=Decimal("482.99"), due=date(2012, 1, 31)) == "458101710000001220004829900000000559582243294671120131"
    assert barcode(iban="FI02 5000 4640 0013 02", reference="69 87567 20834 35364", amount=Decimal("693.80"), due=date(2011, 7, 24)) == "402500046400013020006938000000069875672083435364110724"
    assert barcode(iban="FI15 6601 0001 5306 41", reference="7 75847 47906 47489", amount=Decimal("7444.54"), due=date(2019, 12, 19)) == "415660100015306410074445400000007758474790647489191219"
    assert barcode(iban="FI16 8000 1400 0502 67", reference="78 77767 96566 28687", amount=Decimal("935.85")) == "416800014000502670009358500000078777679656628687000000"
    assert barcode(iban="FI73 3131 3001 0000 58", reference="8 68624", amount=Decimal("0.00"), due=date(2013, 8, 9)) == "473313130010000580000000000000000000000000868624130809"
    assert barcode(iban="FI83 3301 0001 1007 75", reference="92125 37425 25398 97737", amount=Decimal("150000.20"), due=date(2016, 5, 25)) == "483330100011007751500002000092125374252539897737160525"
    assert barcode(iban="FI39 3636 3002 0924 92", reference="5907 38390", amount=Decimal("1.03"), due=date(2023, 3, 11)) == "439363630020924920000010300000000000000590738390230311"
    assert barcode(iban="FI92 3939 0001 0033 91", reference="13 57914", amount=Decimal("0.02"), due=date(2099, 12, 24)) == "492393900010033910000000200000000000000001357914991224"


def test_barcode_invalid_de():
    """Test invalid non-FI IBAN"""
    try:
        barcode(iban="DE79 4405 2020 0360 82", reference="86851 62596 19897", amount=Decimal("4883.15"), due=date(2010, 6, 12))
        assert False, "Barcodes can be printed only for IBANs starting with FI, invalid IBAN was not detected"
    except BarcodeException as e:
        pass


def test_barcode_invalid_amount():
    """Test invalid non-FI IBAN"""
    try:
        barcode(iban="FI79 4405 2020 0360 82", reference="86851 62596 19897", amount=Decimal("1000000.00"), due=date(2010, 6, 12))
        assert False, "Barcode payment amount must be less than 1000000.00, invalid amount was not detected"
    except BarcodeException as e:
        pass
