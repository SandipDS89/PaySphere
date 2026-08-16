from decimal import Decimal
from app import get_valid_amount
import pytest
pytestmark = pytest.mark.unit


def test_valid_positive_amount():
    result = get_valid_amount("500")
    assert result == Decimal("500")


def test_valid_decimal_amount():
    result = get_valid_amount("99.99")
    assert result == Decimal("99.99")


def test_zero_amount_is_invalid():
    result = get_valid_amount("0")
    assert result is None


def test_negative_amount_is_invalid():
    result = get_valid_amount("-100")
    assert result is None


def test_non_numeric_amount_is_invalid():
    result = get_valid_amount("abc")
    assert result is None


def test_empty_string_is_invalid():
    result = get_valid_amount("")
    assert result is None