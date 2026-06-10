"""Tests for ndjson_codec.sort_by() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import sort_by

DATA = b'{"id":3,"name":"c"}\n{"id":1,"name":"a"}\n{"id":2,"name":"b"}\n'


def test_sort_by_int_field():
    result = sort_by(DATA, "id")
    assert [r["id"] for r in result] == [1, 2, 3]


def test_sort_by_string_field():
    result = sort_by(DATA, "name")
    assert [r["name"] for r in result] == ["a", "b", "c"]


def test_sort_descending():
    result = sort_by(DATA, "id", reverse=True)
    assert [r["id"] for r in result] == [3, 2, 1]


def test_missing_field_at_end():
    data = b'{"a":1}\n{"b":2}\n{"a":0}\n'
    result = sort_by(data, "a")
    assert result[0] == {"a": 0}
    assert result[-1] == {"b": 2}


def test_empty_source():
    result = sort_by(b"", "id")
    assert result == []


def test_returns_list():
    result = sort_by(DATA, "id")
    assert isinstance(result, list)


def test_sort_preserves_all_records():
    result = sort_by(DATA, "id")
    assert len(result) == 3
