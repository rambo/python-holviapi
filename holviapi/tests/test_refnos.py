# -*- coding: utf-8 -*-
import random

import pytest

from holviapi.utils import (
    ISO_REFERENCE_VALID,
    fin_reference_isvalid,
    int2fin_reference,
    iso_reference_isvalid,
    str2iso_reference
)


def test_fin_reference_isvalid_valid_results():
    """Test handpicked, known-good inputs"""
    assert fin_reference_isvalid(13)
    assert fin_reference_isvalid(107)
    assert fin_reference_isvalid(105523)
    assert fin_reference_isvalid(102319)
    assert fin_reference_isvalid(108326)
    assert fin_reference_isvalid(100816)
    assert fin_reference_isvalid(108724)
    assert fin_reference_isvalid(108711)


def test_fin_reference_isvalid_invalid_results():
    """Test handpicked, known-bad inputs"""
    assert not fin_reference_isvalid(1071110)
    assert not fin_reference_isvalid(1055110)
    assert not fin_reference_isvalid(1026110)
    assert not fin_reference_isvalid(1039110)
    assert not fin_reference_isvalid(1084110)


def test_int2fin_reference_valid_results():
    """Test handpicked, known-good inputs and corresponding outputs"""
    assert int2fin_reference(1) == '13'
    assert int2fin_reference(10) == '107'
    assert int2fin_reference(10552) == '105523'
    assert int2fin_reference(10231) == '102319'
    assert int2fin_reference(10832) == '108326'
    assert int2fin_reference(10081) == '100816'
    assert int2fin_reference(10872) == '108724'
    assert int2fin_reference(10871) == '108711'


def test_int2fin_reference_invalid_results():
    """Test some invalid values from issue #6"""
    assert int2fin_reference(10711) != '1071110'
    assert int2fin_reference(10551) != '1055110'
    assert int2fin_reference(10261) != '1026110'
    assert int2fin_reference(10391) != '1039110'
    assert int2fin_reference(10841) != '1084110'


def test_int2fin_reference_random_inputs():
    for x in range(1000):
        testint = random.randint(1, 2**24)
        reference = int2fin_reference(testint)
        assert fin_reference_isvalid(reference)


def test_str2iso_reference_valid_results():
    assert str2iso_reference('C2H5OH') == 'RF97C2H5OH'


def test_str2iso_reference_invalid_results():
    assert str2iso_reference('C2H5OH') != 'RF40C2H5OH'


def test_iso_reference_isvalid_valid_results():
    assert iso_reference_isvalid('RF97C2H5OH')


def test_iso_reference_isvalid_invalid_results():
    assert not iso_reference_isvalid('RF40C2H5OH')


def test_str2iso_reference_random_integers():
    for x in range(1000):
        testint = random.randint(1, 2**24)
        reference = str2iso_reference(str(testint))
        assert iso_reference_isvalid(reference)


def test_str2iso_reference_random_strings():
    for x in range(1000):
        teststr = ''
        for y in range(5, 14):
            teststr += random.choice(ISO_REFERENCE_VALID)
        reference = str2iso_reference(teststr)
        assert iso_reference_isvalid(reference)
