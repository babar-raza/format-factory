"""Tests for NDJSON exports added in mainstream-product-deepening-rnext4.

Functions tested: tail, pick, average_value, count_by, distinct_values.

Covers: normal operation, empty sources, boundary cases.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    tail,
    pick,
    average_value,
    count_by,
    distinct_values,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ndjson_bytes(*records) -> bytes:
    import json
    return b"\n".join(json.dumps(r).encode() for r in records) + b"\n"


# ---------------------------------------------------------------------------
# tail
# ---------------------------------------------------------------------------

def test_tail_basic():
    src = _ndjson_bytes({"id": 1}, {"id": 2}, {"id": 3})
    assert tail(src, 2) == [{"id": 2}, {"id": 3}]


def test_tail_all():
    src = _ndjson_bytes({"x": "a"}, {"x": "b"})
    result = tail(src, 5)
    assert result == [{"x": "a"}, {"x": "b"}]


def test_tail_zero_returns_empty():
    src = _ndjson_bytes({"id": 1})
    assert tail(src, 0) == []


def test_tail_empty_source():
    assert tail(b"", 3) == []


def test_tail_returns_list():
    src = _ndjson_bytes({"k": "v"})
    assert isinstance(tail(src, 1), list)


# ---------------------------------------------------------------------------
# pick
# ---------------------------------------------------------------------------

def test_pick_basic():
    src = _ndjson_bytes({"a": 1, "b": 2, "c": 3})
    result = pick(src, ["a", "c"])
    assert result == [{"a": 1, "c": 3}]


def test_pick_missing_field_omitted():
    src = _ndjson_bytes({"a": 1, "b": 2})
    result = pick(src, ["a", "z"])
    assert result == [{"a": 1}]


def test_pick_empty_fields_list():
    src = _ndjson_bytes({"a": 1})
    result = pick(src, [])
    assert result == [{}]


def test_pick_multiple_records():
    src = _ndjson_bytes({"name": "Alice", "age": 30}, {"name": "Bob", "age": 25})
    result = pick(src, ["name"])
    assert result == [{"name": "Alice"}, {"name": "Bob"}]


def test_pick_empty_source():
    assert pick(b"", ["a"]) == []


# ---------------------------------------------------------------------------
# average_value
# ---------------------------------------------------------------------------

def test_average_value_basic():
    src = _ndjson_bytes({"score": 10}, {"score": 20}, {"score": 30})
    assert average_value(src, "score") == 20.0


def test_average_value_skips_missing():
    src = _ndjson_bytes({"score": 5}, {"other": 99}, {"score": 15})
    assert average_value(src, "score") == 10.0


def test_average_value_empty_source():
    assert average_value(b"", "score") == 0.0


def test_average_value_returns_float():
    src = _ndjson_bytes({"n": 4})
    result = average_value(src, "n")
    assert isinstance(result, float)


def test_average_value_no_matching_field():
    src = _ndjson_bytes({"x": 1}, {"y": 2})
    assert average_value(src, "z") == 0.0


# ---------------------------------------------------------------------------
# count_by
# ---------------------------------------------------------------------------

def test_count_by_basic():
    src = _ndjson_bytes({"type": "A"}, {"type": "B"}, {"type": "A"})
    result = count_by(src, "type")
    assert result == {"A": 2, "B": 1}


def test_count_by_skips_missing():
    src = _ndjson_bytes({"type": "X"}, {"other": "y"})
    result = count_by(src, "type")
    assert result == {"X": 1}


def test_count_by_empty_source():
    assert count_by(b"", "type") == {}


def test_count_by_returns_dict():
    result = count_by(_ndjson_bytes({"k": "v"}), "k")
    assert isinstance(result, dict)


def test_count_by_single_group():
    src = _ndjson_bytes({"cat": "Z"}, {"cat": "Z"}, {"cat": "Z"})
    result = count_by(src, "cat")
    assert result == {"Z": 3}


# ---------------------------------------------------------------------------
# distinct_values
# ---------------------------------------------------------------------------

def test_distinct_values_basic():
    src = _ndjson_bytes({"x": "A"}, {"x": "B"}, {"x": "A"})
    result = distinct_values(src, "x")
    assert result == ["A", "B"]


def test_distinct_values_preserves_order():
    src = _ndjson_bytes({"v": 3}, {"v": 1}, {"v": 2}, {"v": 1})
    result = distinct_values(src, "v")
    assert result == [3, 1, 2]


def test_distinct_values_skips_missing_field():
    src = _ndjson_bytes({"x": "A"}, {"y": "B"}, {"x": "C"})
    result = distinct_values(src, "x")
    assert result == ["A", "C"]


def test_distinct_values_empty_source():
    assert distinct_values(b"", "x") == []


def test_distinct_values_returns_list():
    src = _ndjson_bytes({"k": "v"})
    result = distinct_values(src, "k")
    assert isinstance(result, list)
