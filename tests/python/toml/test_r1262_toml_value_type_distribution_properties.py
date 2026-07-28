"""Tests for R1262: TomlDocument value type distribution properties.

Properties under test:
    has_mixed_values  — more than one distinct Python type at top level
    string_key_count  — number of top-level string values
    numeric_key_count — number of top-level numeric (int/float, not bool) values

spec_fact_ref: SAL-TOML-00001
"""

import pytest
from toml.models import TomlDocument


def _make_doc(data: dict) -> TomlDocument:
    return TomlDocument({"data": data})


# ── has_mixed_values ──────────────────────────────────────────────────────────

class TestHasMixedValues:
    def test_empty_doc_not_mixed(self):
        doc = _make_doc({})
        assert doc.has_mixed_values is False

    def test_all_strings_not_mixed(self):
        doc = _make_doc({"a": "x", "b": "y"})
        assert doc.has_mixed_values is False

    def test_string_and_int_is_mixed(self):
        doc = _make_doc({"a": "x", "b": 42})
        assert doc.has_mixed_values is True

    def test_all_ints_not_mixed(self):
        doc = _make_doc({"a": 1, "b": 2, "c": 3})
        assert doc.has_mixed_values is False

    def test_int_and_list_is_mixed(self):
        doc = _make_doc({"a": 1, "b": [1, 2]})
        assert doc.has_mixed_values is True


# ── string_key_count ──────────────────────────────────────────────────────────

class TestStringKeyCount:
    def test_no_strings_zero(self):
        doc = _make_doc({"a": 1, "b": 2})
        assert doc.string_key_count == 0

    def test_all_strings(self):
        doc = _make_doc({"a": "x", "b": "y", "c": "z"})
        assert doc.string_key_count == 3

    def test_mixed_count_strings(self):
        doc = _make_doc({"a": "x", "b": 42, "c": "y"})
        assert doc.string_key_count == 2

    def test_empty_doc_zero(self):
        doc = _make_doc({})
        assert doc.string_key_count == 0

    def test_bool_not_string(self):
        doc = _make_doc({"a": True, "b": "text"})
        assert doc.string_key_count == 1


# ── numeric_key_count ─────────────────────────────────────────────────────────

class TestNumericKeyCount:
    def test_no_numbers_zero(self):
        doc = _make_doc({"a": "x", "b": "y"})
        assert doc.numeric_key_count == 0

    def test_all_ints(self):
        doc = _make_doc({"a": 1, "b": 2, "c": 3})
        assert doc.numeric_key_count == 3

    def test_mixed_count_numbers(self):
        doc = _make_doc({"a": 1, "b": "x", "c": 3.14})
        assert doc.numeric_key_count == 2

    def test_bool_excluded(self):
        doc = _make_doc({"a": True, "b": 42})
        assert doc.numeric_key_count == 1

    def test_float_counts(self):
        doc = _make_doc({"a": 1.5, "b": 2.7})
        assert doc.numeric_key_count == 2

    def test_empty_doc_zero(self):
        doc = _make_doc({})
        assert doc.numeric_key_count == 0


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_mixed_string_and_number_both_count(self):
        doc = _make_doc({"a": "x", "b": 42})
        assert doc.has_mixed_values is True
        assert doc.string_key_count == 1
        assert doc.numeric_key_count == 1

    def test_string_count_plus_numeric_count_le_key_count(self):
        doc = _make_doc({"a": "x", "b": 1, "c": [1, 2], "d": True})
        assert doc.string_key_count + doc.numeric_key_count <= doc.key_count
