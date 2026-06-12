"""
tests/python/ndjson/test_r186_ndjson_null_field_count.py

Tests for ndjson_null_field_count() — count records where a field is null or absent.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
"""
from __future__ import annotations

import pytest

from src.python.ndjson.ndjson_codec import ndjson_null_field_count


class TestNdjsonNullFieldCount:
    def test_all_null(self):
        records = [{"x": None}, {"x": None}, {"x": None}]
        assert ndjson_null_field_count(records, "x") == 3

    def test_none_null(self):
        records = [{"x": 1}, {"x": "hello"}, {"x": 0}]
        assert ndjson_null_field_count(records, "x") == 0

    def test_mixed_null_and_value(self):
        records = [{"x": None}, {"x": 42}, {"x": None}, {"x": "ok"}]
        assert ndjson_null_field_count(records, "x") == 2

    def test_missing_field_counts_as_null(self):
        records = [{"x": 1}, {"y": 2}, {"z": 3}]
        # Only the first record has "x"; others are missing
        assert ndjson_null_field_count(records, "x") == 2

    def test_empty_list(self):
        assert ndjson_null_field_count([], "x") == 0

    def test_field_with_false_not_counted(self):
        records = [{"x": False}, {"x": 0}, {"x": ""}]
        # False, 0, "" are not None — should NOT be counted
        assert ndjson_null_field_count(records, "x") == 0

    def test_non_dict_records_skipped(self):
        records = [{"x": None}, "not_a_dict", 42, {"x": 1}]
        # Only dict records counted; non-dicts skipped
        assert ndjson_null_field_count(records, "x") == 1

    def test_all_records_missing_field(self):
        records = [{"a": 1}, {"b": 2}, {"c": 3}]
        assert ndjson_null_field_count(records, "x") == 3

    def test_single_record_null(self):
        records = [{"score": None}]
        assert ndjson_null_field_count(records, "score") == 1

    def test_nested_null_in_other_fields(self):
        records = [
            {"name": "Alice", "score": 95},
            {"name": None, "score": None},
            {"name": "Bob", "score": 70},
        ]
        assert ndjson_null_field_count(records, "score") == 1
        assert ndjson_null_field_count(records, "name") == 1
