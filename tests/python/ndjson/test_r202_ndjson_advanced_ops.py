"""
tests/python/ndjson/test_r202_ndjson_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT14-001
TASK-001 (part B): NDJSON advanced operations.

Covers: probe_ndjson, load_ndjson, write_ndjson, get_field_names,
get_record_count, sum_field, average_value, count_records, ndjson_record_count,
ndjson_field_exists, ndjson_max_field_count, ndjson_null_field_count,
ndjson_total_field_count, distinct_values, count_unique_values,
head, tail, min_value, max_value, filter_records.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    probe_ndjson, load_ndjson, write_ndjson, get_field_names,
    get_record_count, sum_field, average_value, count_records,
    ndjson_record_count, ndjson_field_exists, ndjson_max_field_count,
    ndjson_null_field_count, ndjson_total_field_count, distinct_values,
    count_unique_values, head, tail, min_value, max_value, filter_records,
)

_DATA = b'{"name":"Alice","score":90}\n{"name":"Bob","score":75}\n{"name":"Carol","score":85}\n'
_SINGLE = b'{"x":1}\n'


class TestNdjsonProbeAndLoad:
    """probe_ndjson, load_ndjson, write_ndjson."""

    def test_probe_ndjson_true(self):
        assert probe_ndjson(_DATA) is True

    def test_probe_ndjson_empty_false_or_bool(self):
        result = probe_ndjson(b"")
        assert isinstance(result, bool)

    def test_load_ndjson_list(self):
        records = load_ndjson(_DATA)
        assert isinstance(records, list)
        assert len(records) == 3

    def test_load_ndjson_records_are_dicts(self):
        records = load_ndjson(_DATA)
        assert all(isinstance(r, dict) for r in records)

    def test_load_ndjson_first_name(self):
        records = load_ndjson(_DATA)
        assert records[0]["name"] == "Alice"

    def test_load_ndjson_single(self):
        records = load_ndjson(_SINGLE)
        assert len(records) == 1

    def test_write_ndjson_to_file(self):
        import tempfile
        import os
        records = load_ndjson(_DATA)
        fd, path = tempfile.mkstemp(suffix=".ndjson")
        os.close(fd)
        try:
            write_ndjson(records, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


class TestNdjsonFieldOps:
    """get_field_names, get_record_count, ndjson_field_exists, ndjson_max_field_count."""

    def test_get_field_names_list(self):
        names = get_field_names(_DATA)
        assert isinstance(names, list)
        assert "name" in names
        assert "score" in names

    def test_get_record_count_three(self):
        assert get_record_count(_DATA) == 3

    def test_ndjson_record_count_three(self):
        assert ndjson_record_count(_DATA) == 3

    def test_count_records_three(self):
        assert count_records(_DATA) == 3

    def test_ndjson_field_exists_true(self):
        assert ndjson_field_exists(_DATA, "score") is True

    def test_ndjson_field_exists_false(self):
        assert ndjson_field_exists(_DATA, "nonexistent_xyz") is False

    def test_ndjson_max_field_count(self):
        n = ndjson_max_field_count(_DATA)
        assert isinstance(n, int)
        assert n == 2

    def test_ndjson_null_field_count_zero(self):
        n = ndjson_null_field_count(_DATA, "score")
        assert n == 0

    def test_ndjson_total_field_count(self):
        n = ndjson_total_field_count(_DATA)
        assert n == 6  # 3 records x 2 fields


class TestNdjsonAnalytics:
    """sum_field, average_value, min_value, max_value, distinct_values, count_unique_values."""

    def test_sum_field_float(self):
        s = sum_field(_DATA, "score")
        assert s == 250.0

    def test_average_value_float(self):
        avg = average_value(_DATA, "score")
        assert isinstance(avg, float)
        assert abs(avg - 83.33) < 0.1

    def test_min_value_int(self):
        m = min_value(_DATA, "score")
        assert m == 75

    def test_max_value_int(self):
        m = max_value(_DATA, "score")
        assert m == 90

    def test_distinct_values_list(self):
        vals = distinct_values(_DATA, "name")
        assert isinstance(vals, list)
        assert len(vals) == 3

    def test_count_unique_values_three(self):
        n = count_unique_values(_DATA, "name")
        assert n == 3


class TestNdjsonSliceOps:
    """head, tail, filter_records."""

    def test_head_two_records(self):
        result = head(_DATA, 2)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"

    def test_tail_one_record(self):
        result = tail(_DATA, 1)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Carol"

    def test_filter_records_returns_list(self):
        # filter_records(source, key, value) → exact match filter
        result = filter_records(_DATA, "name", "Alice")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
