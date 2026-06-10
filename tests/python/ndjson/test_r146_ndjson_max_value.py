"""Tests for ndjson.ndjson_codec.max_value() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import max_value, to_jsonl_str


def _src(records):
    return to_jsonl_str(records).encode()


def test_max_of_numbers():
    src = _src([{"score": 10}, {"score": 30}, {"score": 20}])
    assert max_value(src, "score") == 30


def test_max_of_strings():
    src = _src([{"name": "Alice"}, {"name": "Charlie"}, {"name": "Bob"}])
    assert max_value(src, "name") == "Charlie"


def test_empty_returns_none():
    assert max_value(_src([]), "score") is None


def test_missing_field_returns_none():
    src = _src([{"other": 1}, {"other": 2}])
    assert max_value(src, "score") is None


def test_single_record():
    src = _src([{"v": 42}])
    assert max_value(src, "v") == 42


def test_skips_missing_field():
    src = _src([{"v": 5}, {"x": 99}, {"v": 3}])
    assert max_value(src, "v") == 5
