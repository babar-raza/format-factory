"""Tests for ndjson.ndjson_codec.sum_field() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import sum_field, to_jsonl_str


def _src(records):
    return to_jsonl_str(records).encode()


def test_sum_three_values():
    src = _src([{"v": 10}, {"v": 20}, {"v": 30}])
    assert sum_field(src, "v") == 60.0


def test_non_numeric_skipped():
    src = _src([{"v": 10}, {"v": "bad"}, {"v": 20}])
    assert sum_field(src, "v") == 30.0


def test_missing_field_skipped():
    src = _src([{"v": 5}, {"x": 99}, {"v": 15}])
    assert sum_field(src, "v") == 20.0


def test_no_values_returns_zero():
    src = _src([{"x": 1}])
    assert sum_field(src, "v") == 0.0


def test_returns_float():
    src = _src([{"v": 5}])
    assert isinstance(sum_field(src, "v"), float)
