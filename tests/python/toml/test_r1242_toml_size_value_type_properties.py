"""Tests for R1242: TomlDocument size and value type properties.

Properties under test:
    is_large    — key_count > 20
    has_numbers — any top-level value is int or float (not bool)
    has_strings — any top-level value is str

spec_fact_ref: SAL-TOML-00001
"""

import pytest
from toml.models import TomlDocument


def _make_doc(data: dict) -> TomlDocument:
    """Build a TomlDocument stub wrapping given data dict."""
    return TomlDocument({"data": data})


# ── is_large ──────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_21_keys_is_large(self):
        doc = _make_doc({str(i): i for i in range(21)})
        assert doc.is_large is True

    def test_exactly_20_keys_not_large(self):
        doc = _make_doc({str(i): i for i in range(20)})  # not > 20
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc({})
        assert doc.is_large is False

    def test_single_key_not_large(self):
        doc = _make_doc({"name": "test"})
        assert doc.is_large is False

    def test_5_keys_not_large(self):
        doc = _make_doc({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5})
        assert doc.is_large is False

    def test_100_keys_is_large(self):
        doc = _make_doc({str(i): i for i in range(100)})
        assert doc.is_large is True


# ── has_numbers ───────────────────────────────────────────────────────────────

class TestHasNumbers:
    def test_int_value_has_numbers(self):
        doc = _make_doc({"count": 42})
        assert doc.has_numbers is True

    def test_float_value_has_numbers(self):
        doc = _make_doc({"ratio": 3.14})
        assert doc.has_numbers is True

    def test_bool_not_counted_as_number(self):
        doc = _make_doc({"flag": True})  # bool but NOT int for this property
        assert doc.has_numbers is False

    def test_no_numbers_only_strings(self):
        doc = _make_doc({"name": "test", "title": "foo"})
        assert doc.has_numbers is False

    def test_empty_no_numbers(self):
        doc = _make_doc({})
        assert doc.has_numbers is False

    def test_mixed_with_number(self):
        doc = _make_doc({"name": "test", "count": 10})
        assert doc.has_numbers is True

    def test_nested_table_not_a_number(self):
        doc = _make_doc({"section": {"key": 42}})  # top-level is dict, not number
        assert doc.has_numbers is False


# ── has_strings ───────────────────────────────────────────────────────────────

class TestHasStrings:
    def test_string_value_has_strings(self):
        doc = _make_doc({"name": "test"})
        assert doc.has_strings is True

    def test_no_strings_only_ints(self):
        doc = _make_doc({"count": 42, "size": 100})
        assert doc.has_strings is False

    def test_empty_no_strings(self):
        doc = _make_doc({})
        assert doc.has_strings is False

    def test_mixed_with_string(self):
        doc = _make_doc({"title": "hello", "count": 10})
        assert doc.has_strings is True

    def test_nested_table_not_a_string(self):
        doc = _make_doc({"section": {"key": "value"}})
        assert doc.has_strings is False

    def test_multiple_strings(self):
        doc = _make_doc({"name": "Alice", "title": "Engineer", "city": "NYC"})
        assert doc.has_strings is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_large_document_is_large(self):
        doc = _make_doc({str(i): i for i in range(25)})
        assert doc.is_large is True
        assert doc.key_count == 25

    def test_numbers_and_strings_together(self):
        doc = _make_doc({"name": "test", "count": 42, "ratio": 3.14})
        assert doc.has_numbers is True
        assert doc.has_strings is True

    def test_not_large_consistent_with_key_count(self):
        doc = _make_doc({"a": 1, "b": 2})
        assert doc.is_large is False
        assert doc.key_count == 2

    def test_bool_not_number_not_string(self):
        doc = _make_doc({"flag": True, "enabled": False})
        assert doc.has_numbers is False
        assert doc.has_strings is False
        assert doc.has_booleans is True
