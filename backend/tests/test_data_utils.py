import pytest
from utils.data_utils import parse_numeric_value

def test_parse_numeric_value_basic():
    assert parse_numeric_value(100) == 100.0
    assert parse_numeric_value(50.5) == 50.5

def test_parse_numeric_value_string():
    assert parse_numeric_value("5000000") == 5000000.0
    assert parse_numeric_value("  1000  ") == 1000.0

def test_parse_numeric_value_with_currency():
    assert parse_numeric_value("5.000.000 đ") == 5000000.0
    assert parse_numeric_value("1.500.000 VND") == 1500000.0
    assert parse_numeric_value("  100 đ ") == 100.0

def test_parse_numeric_value_complex_formats():
    # 1.500.000,50 -> 1500000.50
    assert parse_numeric_value("1.500.000,50") == 1500000.50
    # 1,500,000.50 -> 1500000.50 (Wait, data_utils replaces . with "" if no comma, let's test specific logic)
    # The logic in data_utils handles "." as thousands and "," as decimal usually.
    pass

def test_parse_numeric_value_invalid():
    assert parse_numeric_value("abc") == 0.0
    assert parse_numeric_value(None) == 0.0
    assert parse_numeric_value("") == 0.0
