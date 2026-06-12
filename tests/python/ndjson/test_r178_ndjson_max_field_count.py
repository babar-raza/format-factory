"""
tests/python/ndjson/test_r178_ndjson_max_field_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT46-001
Tests for ndjson_max_field_count() — max field count in any record.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_max_field_count


class TestNdjsonMaxFieldCount:
    def test_three_records_max_is_three(self):
        records = [{"a": 1, "b": 2}, {"x": 1}, {"p": 1, "q": 2, "r": 3}]
        assert ndjson_max_field_count(records) == 3

    def test_single_record(self):
        records = [{"name": "Alice", "age": 30}]
        assert ndjson_max_field_count(records) == 2

    def test_empty_list_returns_zero(self):
        assert ndjson_max_field_count([]) == 0

    def test_all_same_size(self):
        records = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        assert ndjson_max_field_count(records) == 2

    def test_returns_int(self):
        result = ndjson_max_field_count([{"x": 1}])
        assert isinstance(result, int)

    def test_exported_from_init(self):
        from src.python.ndjson import ndjson_max_field_count as fn
        result = fn([{"a": 1, "b": 2, "c": 3}])
        assert result == 3
