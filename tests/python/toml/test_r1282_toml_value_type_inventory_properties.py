"""Tests for R1282: TomlDocument value type inventory properties.

Properties under test:
    boolean_key_count — number of top-level boolean keys
    list_key_count    — number of top-level list/array keys
    max_array_length  — max length of any top-level list value

spec_fact_ref: SAL-TOML-00001
"""

import pytest
from toml.models import TomlDocument


def _make_doc(data: dict) -> TomlDocument:
    return TomlDocument({"data": data})


# ── boolean_key_count ─────────────────────────────────────────────────────────

class TestBooleanKeyCount:
    def test_empty_doc_zero(self):
        doc = _make_doc({})
        assert doc.boolean_key_count == 0

    def test_no_booleans_zero(self):
        doc = _make_doc({"name": "foo", "count": 5})
        assert doc.boolean_key_count == 0

    def test_one_boolean(self):
        doc = _make_doc({"enabled": True, "name": "foo"})
        assert doc.boolean_key_count == 1

    def test_two_booleans(self):
        doc = _make_doc({"enabled": True, "debug": False, "name": "foo"})
        assert doc.boolean_key_count == 2

    def test_all_booleans(self):
        doc = _make_doc({"a": True, "b": False, "c": True})
        assert doc.boolean_key_count == 3

    def test_int_not_counted_as_bool(self):
        # In Python isinstance(1, bool) is True because bool subclasses int,
        # but our property checks isinstance(v, bool) which is correct for True/False
        doc = _make_doc({"flag": True, "count": 1})
        assert doc.boolean_key_count == 1


# ── list_key_count ────────────────────────────────────────────────────────────

class TestListKeyCount:
    def test_empty_doc_zero(self):
        doc = _make_doc({})
        assert doc.list_key_count == 0

    def test_no_lists_zero(self):
        doc = _make_doc({"name": "foo", "count": 5})
        assert doc.list_key_count == 0

    def test_one_list(self):
        doc = _make_doc({"tags": ["a", "b"], "name": "foo"})
        assert doc.list_key_count == 1

    def test_two_lists(self):
        doc = _make_doc({"tags": ["a", "b"], "ids": [1, 2, 3], "name": "foo"})
        assert doc.list_key_count == 2

    def test_all_lists(self):
        doc = _make_doc({"a": [1], "b": [2, 3], "c": []})
        assert doc.list_key_count == 3


# ── max_array_length ──────────────────────────────────────────────────────────

class TestMaxArrayLength:
    def test_no_lists_returns_zero(self):
        doc = _make_doc({"name": "foo"})
        assert doc.max_array_length == 0

    def test_empty_doc_returns_zero(self):
        doc = _make_doc({})
        assert doc.max_array_length == 0

    def test_single_empty_list_zero(self):
        doc = _make_doc({"tags": []})
        assert doc.max_array_length == 0

    def test_single_list(self):
        doc = _make_doc({"tags": ["a", "b", "c"]})
        assert doc.max_array_length == 3

    def test_two_lists_returns_max(self):
        doc = _make_doc({"short": [1], "long": [1, 2, 3, 4, 5]})
        assert doc.max_array_length == 5

    def test_multiple_lists_returns_max(self):
        doc = _make_doc({"a": [1, 2], "b": [1, 2, 3], "c": [1]})
        assert doc.max_array_length == 3


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_list_key_count_nonzero_implies_max_array_length_exists(self):
        doc = _make_doc({"tags": ["x", "y"]})
        assert doc.list_key_count > 0
        assert doc.max_array_length >= 0

    def test_no_lists_max_array_length_zero(self):
        doc = _make_doc({"enabled": True, "count": 5})
        assert doc.list_key_count == 0
        assert doc.max_array_length == 0

    def test_combined_types(self):
        doc = _make_doc({"flag": True, "items": [1, 2, 3], "name": "foo", "ids": [4, 5]})
        assert doc.boolean_key_count == 1
        assert doc.list_key_count == 2
        assert doc.max_array_length == 3
