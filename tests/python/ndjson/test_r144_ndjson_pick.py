"""Tests for ndjson.ndjson_codec.pick() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import pick, to_jsonl_str

RECORDS = [
    {"name": "Alice", "age": 30, "city": "London"},
    {"name": "Bob", "age": 25, "city": "Paris"},
]


def _make_source(records):
    return to_jsonl_str(records).encode()


def test_pick_single_field():
    src = _make_source(RECORDS)
    result = pick(src, ["name"])
    assert result == [{"name": "Alice"}, {"name": "Bob"}]


def test_pick_multiple_fields():
    src = _make_source(RECORDS)
    result = pick(src, ["name", "age"])
    assert result[0] == {"name": "Alice", "age": 30}


def test_missing_field_omitted():
    src = _make_source([{"a": 1, "b": 2}, {"b": 3}])
    result = pick(src, ["a"])
    assert result[0] == {"a": 1}
    assert result[1] == {}


def test_empty_fields_returns_empty_dicts():
    src = _make_source(RECORDS)
    result = pick(src, [])
    assert result == [{}, {}]


def test_returns_list():
    src = _make_source(RECORDS)
    assert isinstance(pick(src, ["name"]), list)


def test_count_unchanged():
    src = _make_source(RECORDS)
    assert len(pick(src, ["name"])) == 2
