"""Tests for ndjson_codec.tail() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import tail

FIVE_RECORDS = b'{"id":1}\n{"id":2}\n{"id":3}\n{"id":4}\n{"id":5}\n'


def test_tail_basic():
    result = tail(FIVE_RECORDS, 3)
    assert len(result) == 3
    assert result[0] == {"id": 3}
    assert result[-1] == {"id": 5}


def test_tail_zero_returns_empty():
    result = tail(FIVE_RECORDS, 0)
    assert result == []


def test_tail_larger_than_source():
    result = tail(FIVE_RECORDS, 100)
    assert len(result) == 5


def test_tail_equals_count():
    result = tail(FIVE_RECORDS, 5)
    assert len(result) == 5


def test_tail_one():
    result = tail(FIVE_RECORDS, 1)
    assert len(result) == 1
    assert result[0] == {"id": 5}


def test_tail_empty_source():
    result = tail(b"", 3)
    assert result == []


def test_tail_negative_raises():
    try:
        tail(FIVE_RECORDS, -1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_tail_string_source():
    ndjson = '{"x":10}\n{"x":20}\n{"x":30}\n'
    result = tail(ndjson, 2)
    assert len(result) == 2
    assert result[0] == {"x": 20}
