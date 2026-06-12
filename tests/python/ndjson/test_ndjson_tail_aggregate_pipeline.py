"""
test_ndjson_tail_aggregate_pipeline.py -- NDJSON tail + aggregate pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-93
Tests tail returns list, tail count=2, aggregate sum float, aggregate max value,
aggregate count matches records.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import write_ndjson, tail, aggregate

_RECORDS = [
    {"name": "Alice", "score": 80},
    {"name": "Bob", "score": 60},
    {"name": "Carol", "score": 90},
    {"name": "Dave", "score": 70},
]


def test_tail_returns_list(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = tail(str(dest), 2)
    assert isinstance(result, list)


def test_tail_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = tail(str(dest), 2)
    assert len(result) == 2


def test_aggregate_sum_float(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = aggregate(str(dest), "score", "sum")
    assert isinstance(result, (int, float))
    assert result == 300


def test_aggregate_max_value(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = aggregate(str(dest), "score", "max")
    assert result == 90


def test_tail_last_record(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = tail(str(dest), 1)
    assert result[0]["name"] == "Dave"
