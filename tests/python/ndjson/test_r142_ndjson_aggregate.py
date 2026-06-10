"""Tests for ndjson_codec.aggregate() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import aggregate

DATA = b'{"v":10}\n{"v":20}\n{"v":30}\n'


def test_sum():
    assert aggregate(DATA, "v", "sum") == 60


def test_count():
    assert aggregate(DATA, "v", "count") == 3


def test_min():
    assert aggregate(DATA, "v", "min") == 10


def test_max():
    assert aggregate(DATA, "v", "max") == 30


def test_count_empty():
    assert aggregate(b"", "v", "count") == 0


def test_sum_missing_field_returns_none():
    data = b'{"x":1}\n{"y":2}\n'
    assert aggregate(data, "v", "sum") is None


def test_invalid_func_raises():
    try:
        aggregate(DATA, "v", "average")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_sum_skips_nonnumeric():
    data = b'{"v":10}\n{"v":"text"}\n{"v":5}\n'
    assert aggregate(data, "v", "sum") == 15
