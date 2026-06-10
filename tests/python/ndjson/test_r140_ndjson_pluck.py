"""Tests for ndjson_codec.pluck() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import pluck

RECORDS = b'{"name":"Alice","age":30}\n{"name":"Bob","age":25}\n{"name":"Charlie","age":40}\n'


def test_pluck_string_field():
    result = pluck(RECORDS, "name")
    assert result == ["Alice", "Bob", "Charlie"]


def test_pluck_int_field():
    result = pluck(RECORDS, "age")
    assert result == [30, 25, 40]


def test_pluck_missing_field_skipped():
    data = b'{"a":1}\n{"b":2}\n{"a":3}\n'
    result = pluck(data, "a")
    assert result == [1, 3]


def test_pluck_empty_source():
    result = pluck(b"", "name")
    assert result == []


def test_pluck_nondict_records_skipped():
    data = b'"string"\n{"name":"x"}\n42\n'
    result = pluck(data, "name")
    assert result == ["x"]


def test_pluck_returns_list():
    result = pluck(RECORDS, "name")
    assert isinstance(result, list)


def test_pluck_all_missing():
    result = pluck(RECORDS, "nonexistent")
    assert result == []


def test_pluck_preserves_order():
    data = b'{"v":3}\n{"v":1}\n{"v":2}\n'
    result = pluck(data, "v")
    assert result == [3, 1, 2]
