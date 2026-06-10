"""Tests for NDJSON exports added in mainstream-product-deepening-rnext6.

Functions tested: count_records, zip_records, sort_by, aggregate.

Covers: normal operation, empty sources, boundary cases.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    count_records,
    zip_records,
    sort_by,
    aggregate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ndjson_bytes(*records) -> bytes:
    import json
    return b"\n".join(json.dumps(r).encode() for r in records) + b"\n"


# ---------------------------------------------------------------------------
# count_records
# ---------------------------------------------------------------------------

def test_count_records_basic():
    src = _ndjson_bytes({"id": 1}, {"id": 2}, {"id": 3})
    assert count_records(src) == 3


def test_count_records_empty():
    assert count_records(b"") == 0


def test_count_records_returns_int():
    src = _ndjson_bytes({"k": "v"})
    assert isinstance(count_records(src), int)


def test_count_records_single():
    src = _ndjson_bytes({"a": 1})
    assert count_records(src) == 1


def test_count_records_many():
    recs = [{"i": i} for i in range(10)]
    import json
    src = b"\n".join(json.dumps(r).encode() for r in recs)
    assert count_records(src) == 10


# ---------------------------------------------------------------------------
# zip_records
# ---------------------------------------------------------------------------

def test_zip_records_basic():
    a = [{"x": 1}, {"x": 2}]
    b = [{"y": 10}, {"y": 20}]
    result = zip_records(a, b)
    assert result == [{"x": 1, "y": 10}, {"x": 2, "y": 20}]


def test_zip_records_stops_at_shorter():
    a = [{"x": 1}, {"x": 2}, {"x": 3}]
    b = [{"y": 10}]
    result = zip_records(a, b)
    assert len(result) == 1


def test_zip_records_second_overwrites():
    a = [{"k": "old"}]
    b = [{"k": "new"}]
    result = zip_records(a, b)
    assert result == [{"k": "new"}]


def test_zip_records_empty_lists():
    assert zip_records([], []) == []


def test_zip_records_returns_list():
    assert isinstance(zip_records([{"a": 1}], [{"b": 2}]), list)


# ---------------------------------------------------------------------------
# sort_by
# ---------------------------------------------------------------------------

def test_sort_by_basic():
    src = _ndjson_bytes({"n": 3}, {"n": 1}, {"n": 2})
    result = sort_by(src, "n")
    assert [r["n"] for r in result] == [1, 2, 3]


def test_sort_by_reverse():
    src = _ndjson_bytes({"n": 1}, {"n": 3}, {"n": 2})
    result = sort_by(src, "n", reverse=True)
    assert [r["n"] for r in result] == [3, 2, 1]


def test_sort_by_strings():
    src = _ndjson_bytes({"s": "b"}, {"s": "a"}, {"s": "c"})
    result = sort_by(src, "s")
    assert [r["s"] for r in result] == ["a", "b", "c"]


def test_sort_by_empty_source():
    assert sort_by(b"", "n") == []


def test_sort_by_returns_list():
    src = _ndjson_bytes({"k": 1})
    assert isinstance(sort_by(src, "k"), list)


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------

def test_aggregate_sum():
    src = _ndjson_bytes({"n": 10}, {"n": 20}, {"n": 30})
    result = aggregate(src, "n", "sum")
    assert result == 60


def test_aggregate_count():
    src = _ndjson_bytes({"n": 1}, {"n": 2})
    assert aggregate(src, "n", "count") == 2


def test_aggregate_min():
    src = _ndjson_bytes({"n": 5}, {"n": 2}, {"n": 8})
    assert aggregate(src, "n", "min") == 2


def test_aggregate_max():
    src = _ndjson_bytes({"n": 5}, {"n": 2}, {"n": 8})
    assert aggregate(src, "n", "max") == 8


def test_aggregate_invalid_func_raises():
    src = _ndjson_bytes({"n": 1})
    with pytest.raises(ValueError):
        aggregate(src, "n", "product")
