"""
tests/python/dif/test_r186_dif_total_numeric_count.py

Tests for dif_total_numeric_count() — count total numeric-type cells in a DIF document.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
"""
from __future__ import annotations

import pytest

from src.python.dif.dif_stats import dif_total_numeric_count


def _make_doc(rows):
    """Build a minimal DIF-style document dict."""
    return {"rows": rows, "title": "test", "vectors": 0, "tuples": 0}


def _cell(value, ctype):
    return {"value": value, "type": ctype}


class TestDifTotalNumericCount:
    def test_all_numeric_type(self):
        doc = _make_doc([
            [_cell(1, "numeric"), _cell(2, "numeric")],
            [_cell(3, "numeric"), _cell(4, "numeric")],
        ])
        assert dif_total_numeric_count(doc) == 4

    def test_no_numeric_cells(self):
        doc = _make_doc([
            [_cell("foo", "string"), _cell("bar", "text")],
        ])
        assert dif_total_numeric_count(doc) == 0

    def test_mixed_types(self):
        doc = _make_doc([
            [_cell("name", "string"), _cell(42, "numeric"), _cell("city", "text")],
            [_cell("Alice", "string"), _cell(30, "numeric"), _cell("London", "text")],
        ])
        assert dif_total_numeric_count(doc) == 2

    def test_int_value_no_type_counts(self):
        # If value is an int/float, it should count even if type is not "numeric"
        doc = _make_doc([
            [{"value": 100, "type": ""}, {"value": "text", "type": ""}],
        ])
        assert dif_total_numeric_count(doc) == 1

    def test_float_value_counts(self):
        doc = _make_doc([
            [_cell(3.14, "numeric"), _cell(2.718, "number")],
        ])
        assert dif_total_numeric_count(doc) == 2

    def test_empty_doc(self):
        assert dif_total_numeric_count({"rows": []}) == 0

    def test_none_value_with_numeric_type(self):
        doc = _make_doc([
            [_cell(None, "numeric")],
        ])
        # None value but type is "numeric" — counts as numeric
        assert dif_total_numeric_count(doc) == 1

    def test_string_type_not_counted(self):
        doc = _make_doc([
            [_cell("hello", "string"), _cell("world", "text")],
        ])
        assert dif_total_numeric_count(doc) == 0

    def test_number_type_alias(self):
        doc = _make_doc([
            [_cell(5, "number"), _cell(6, "numeric")],
        ])
        assert dif_total_numeric_count(doc) == 2

    def test_single_numeric_cell(self):
        doc = _make_doc([[_cell(99, "numeric")]])
        assert dif_total_numeric_count(doc) == 1
