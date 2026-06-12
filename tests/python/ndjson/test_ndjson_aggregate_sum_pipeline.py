"""
test_ndjson_aggregate_sum_pipeline.py -- NDJSON aggregate + sum pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-57
Tests aggregate sum, aggregate count, aggregate max, sum_field float,
aggregate min.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    aggregate,
    sum_field,
)

_RECORDS = [
    {"id": 1, "score": 80, "dept": "eng"},
    {"id": 2, "score": 90, "dept": "mkt"},
    {"id": 3, "score": 70, "dept": "eng"},
    {"id": 4, "score": 60, "dept": "hr"},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_aggregate_sum():
    result = aggregate(_SOURCE, "score", "sum")
    assert result == 300


def test_aggregate_count():
    result = aggregate(_SOURCE, "score", "count")
    assert result == 4


def test_aggregate_max():
    result = aggregate(_SOURCE, "score", "max")
    assert result == 90


def test_sum_field_float():
    result = sum_field(_SOURCE, "score")
    assert isinstance(result, float)
    assert result == 300.0


def test_aggregate_min():
    result = aggregate(_SOURCE, "score", "min")
    assert result == 60
