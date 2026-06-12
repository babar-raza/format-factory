"""
tests/python/ndjson/test_r184_ndjson_average_field_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT52-001
Tests for ndjson_average_field_count() — average number of fields per record.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_average_field_count


class TestNdjsonAverageFieldCount:
    def test_equal_fields_returns_exact_count(self):
        records = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        result = ndjson_average_field_count(records)
        assert result == 2.0

    def test_varying_fields_returns_average(self):
        records = [{"a": 1, "b": 2, "c": 3}, {"x": 4, "y": 5}]
        result = ndjson_average_field_count(records)
        assert result == 2.5

    def test_empty_list_returns_zero(self):
        result = ndjson_average_field_count([])
        assert result == 0.0

    def test_returns_float(self):
        records = [{"a": 1, "b": 2}]
        result = ndjson_average_field_count(records)
        assert isinstance(result, float)

    def test_single_record_equals_its_field_count(self):
        records = [{"a": 1, "b": 2, "c": 3, "d": 4}]
        result = ndjson_average_field_count(records)
        assert result == 4.0

    def test_exported_from_init(self):
        from src.python.ndjson import ndjson_average_field_count as fn
        records = [{"x": 1}, {"y": 2, "z": 3}]
        result = fn(records)
        assert result == 1.5
