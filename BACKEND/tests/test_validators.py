"""
test_validators.py — Unit tests for BACKEND/validators.py

Each test is isolated: no database or Flask context required.
"""

import pytest
import sys
import os

# Ensure BACKEND/ is on the path when running pytest from the BACKEND/ dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validators import validate_amount


class TestValidateAmount:
    """Tests covering every rule in validate_amount()."""

    # --- Presence checks --------------------------------------------------

    def test_none_value_returns_error(self):
        amount, error = validate_amount(None)
        assert amount is None
        assert "required" in error.lower()

    def test_empty_string_returns_error(self):
        amount, error = validate_amount("")
        assert amount is None
        assert "required" in error.lower()

    def test_whitespace_only_returns_error(self):
        amount, error = validate_amount("   ")
        assert amount is None
        assert "required" in error.lower()

    # --- Numeric checks ---------------------------------------------------

    def test_non_numeric_string_returns_error(self):
        amount, error = validate_amount("abc")
        assert amount is None
        assert "number" in error.lower()

    def test_special_chars_return_error(self):
        amount, error = validate_amount("$100")
        assert amount is None
        assert "number" in error.lower()

    # --- Positive checks --------------------------------------------------

    def test_zero_returns_error(self):
        amount, error = validate_amount("0")
        assert amount is None
        assert "greater than zero" in error.lower()

    def test_negative_value_returns_error(self):
        amount, error = validate_amount("-50")
        assert amount is None
        assert "greater than zero" in error.lower()

    def test_negative_decimal_returns_error(self):
        amount, error = validate_amount("-0.01")
        assert amount is None
        assert "greater than zero" in error.lower()

    # --- Decimal precision checks -----------------------------------------

    def test_three_decimal_places_returns_error(self):
        amount, error = validate_amount("10.123")
        assert amount is None
        assert "decimal" in error.lower()

    def test_four_decimal_places_returns_error(self):
        amount, error = validate_amount("10.1234")
        assert amount is None
        assert "decimal" in error.lower()

    # --- Success cases ----------------------------------------------------

    def test_integer_string_is_valid(self):
        amount, error = validate_amount("100")
        assert error is None
        assert amount == 100.0

    def test_one_decimal_place_is_valid(self):
        amount, error = validate_amount("99.9")
        assert error is None
        assert amount == 99.9

    def test_two_decimal_places_is_valid(self):
        amount, error = validate_amount("250.75")
        assert error is None
        assert amount == 250.75

    def test_minimum_valid_amount(self):
        amount, error = validate_amount("0.01")
        assert error is None
        assert amount == 0.01

    def test_large_valid_amount(self):
        amount, error = validate_amount("999999.99")
        assert error is None
        assert amount == 999999.99
