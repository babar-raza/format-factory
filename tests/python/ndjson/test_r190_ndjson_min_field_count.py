"""
tests/python/ndjson/test_r190_ndjson_min_field_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for ndjson_min_field_count() — minimum number of fields in any dict record.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_min_field_count


class TestNdjsonMinFieldCount:
    def test_empty_list_returns_zero(self):
        """Empty list → 0 (no records)."""
        assert ndjson_min_field_count([]) == 0

    def test_single_record(self):
        """Single record → field count of that record."""
        assert ndjson_min_field_count([{"a": 1, "b": 2}]) == 2

    def test_multiple_records_returns_minimum(self):
        """Returns the minimum field count across records."""
        records = [{"a": 1, "b": 2, "c": 3}, {"x": 1}]
        assert ndjson_min_field_count(records) == 1

    def test_all_same_field_count(self):
        """All records with 2 fields → minimum is 2."""
        records = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        assert ndjson_min_field_count(records) == 2

    def test_non_dict_records_ignored(self):
        """Non-dict records (e.g. strings, ints) are ignored."""
        records = [{"a": 1, "b": 2, "c": 3}, "not a dict", 42]
        assert ndjson_min_field_count(records) == 3

    def test_result_is_int(self):
        """Result is always an integer."""
        result = ndjson_min_field_count([{"a": 1}])
        assert isinstance(result, int)
