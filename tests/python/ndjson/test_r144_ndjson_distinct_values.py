"""Tests for ndjson.ndjson_codec.distinct_values() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import distinct_values, to_jsonl_str

RECORDS = [
    {"city": "London", "country": "UK"},
    {"city": "Paris", "country": "FR"},
    {"city": "London", "country": "UK"},
    {"city": "Berlin", "country": "DE"},
]


def _make_source(records):
    return to_jsonl_str(records).encode()


def test_distinct_with_duplicates():
    src = _make_source(RECORDS)
    result = distinct_values(src, "city")
    assert result == ["London", "Paris", "Berlin"]


def test_no_duplicates():
    src = _make_source(RECORDS)
    result = distinct_values(src, "country")
    assert "UK" in result
    assert "FR" in result
    assert result.count("UK") == 1


def test_missing_field_skipped():
    src = _make_source([{"a": 1}, {"b": 2}, {"a": 3}])
    result = distinct_values(src, "a")
    assert result == [1, 3]


def test_empty_returns_empty():
    src = _make_source([])
    assert distinct_values(src, "field") == []


def test_returns_list():
    src = _make_source(RECORDS)
    assert isinstance(distinct_values(src, "city"), list)


def test_order_of_first_occurrence():
    src = _make_source([{"x": "b"}, {"x": "a"}, {"x": "b"}, {"x": "c"}])
    result = distinct_values(src, "x")
    assert result == ["b", "a", "c"]
