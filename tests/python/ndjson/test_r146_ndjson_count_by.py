"""Tests for ndjson.ndjson_codec.count_by() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import count_by, to_jsonl_str

RECORDS = [
    {"city": "London"},
    {"city": "Paris"},
    {"city": "London"},
    {"city": "Berlin"},
    {"city": "Paris"},
    {"city": "London"},
]


def _src(records):
    return to_jsonl_str(records).encode()


def test_count_frequencies():
    result = count_by(_src(RECORDS), "city")
    assert result["London"] == 3
    assert result["Paris"] == 2
    assert result["Berlin"] == 1


def test_returns_dict():
    assert isinstance(count_by(_src(RECORDS), "city"), dict)


def test_missing_field_skipped():
    src = _src([{"a": 1}, {"b": 2}, {"a": 1}])
    result = count_by(src, "a")
    assert result == {1: 2}


def test_empty_source():
    result = count_by(_src([]), "field")
    assert result == {}


def test_single_unique():
    src = _src([{"x": "v"}, {"x": "v"}])
    result = count_by(src, "x")
    assert result == {"v": 2}
