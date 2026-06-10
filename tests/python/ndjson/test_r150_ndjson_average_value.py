"""Tests for ndjson.ndjson_codec.average_value() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import average_value, to_jsonl_str


def _src(records):
    return to_jsonl_str(records).encode()


def test_average_of_three():
    src = _src([{"v": 10}, {"v": 20}, {"v": 30}])
    assert average_value(src, "v") == 20.0


def test_non_numeric_skipped():
    src = _src([{"v": 10}, {"v": "bad"}, {"v": 30}])
    assert average_value(src, "v") == 20.0


def test_missing_field_skipped():
    src = _src([{"v": 10}, {"x": 5}, {"v": 20}])
    assert average_value(src, "v") == 15.0


def test_no_values_returns_zero():
    src = _src([{"x": 1}, {"x": 2}])
    assert average_value(src, "v") == 0.0


def test_returns_float():
    src = _src([{"v": 5}])
    assert isinstance(average_value(src, "v"), float)
