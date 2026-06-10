"""Tests for ndjson.ndjson_codec.min_value() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import min_value, to_jsonl_str


def _src(records):
    return to_jsonl_str(records).encode()


def test_min_of_numbers():
    src = _src([{"score": 30}, {"score": 10}, {"score": 20}])
    assert min_value(src, "score") == 10


def test_min_of_strings():
    src = _src([{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}])
    assert min_value(src, "name") == "Alice"


def test_empty_returns_none():
    assert min_value(_src([]), "score") is None


def test_missing_field_returns_none():
    src = _src([{"other": 1}])
    assert min_value(src, "score") is None


def test_single_record():
    src = _src([{"v": 42}])
    assert min_value(src, "v") == 42


def test_skips_missing_field():
    src = _src([{"v": 5}, {"x": 99}, {"v": 3}])
    assert min_value(src, "v") == 3
