"""Tests for ndjson.ndjson_codec.zip_records() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import zip_records

LIST_A = [{"name": "Alice"}, {"name": "Bob"}]
LIST_B = [{"age": 30}, {"age": 25}]


def test_merges_fields():
    result = zip_records(LIST_A, LIST_B)
    assert result[0] == {"name": "Alice", "age": 30}
    assert result[1] == {"name": "Bob", "age": 25}


def test_stops_at_shorter():
    a = [{"x": 1}, {"x": 2}, {"x": 3}]
    b = [{"y": 10}]
    result = zip_records(a, b)
    assert len(result) == 1


def test_empty_lists():
    assert zip_records([], []) == []


def test_second_overwrites_first_on_collision():
    a = [{"key": "old"}]
    b = [{"key": "new"}]
    result = zip_records(a, b)
    assert result[0]["key"] == "new"


def test_returns_list():
    assert isinstance(zip_records(LIST_A, LIST_B), list)
