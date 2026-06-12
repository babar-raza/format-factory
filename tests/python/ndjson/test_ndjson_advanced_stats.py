"""
test_ndjson_advanced_stats.py -- NDJSON advanced statistics functions.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-26
Tests average_value, min_value, max_value, field_stats count/mean
across a fixed set of records.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    average_value,
    min_value,
    max_value,
    field_stats,
    sum_field,
)

_RECORDS = [
    {"name": "Alice", "score": 90},
    {"name": "Bob", "score": 70},
    {"name": "Carol", "score": 80},
    {"name": "Dave", "score": 100},
    {"name": "Eve", "score": 60},
]


def _write_records(tmp_path):
    dest = tmp_path / "stats.ndjson"
    write_ndjson(_RECORDS, str(dest))
    return dest


def test_average_value_score(tmp_path):
    dest = _write_records(tmp_path)
    avg = average_value(str(dest), "score")
    assert avg == 80.0


def test_min_value_score(tmp_path):
    dest = _write_records(tmp_path)
    assert min_value(str(dest), "score") == 60


def test_max_value_score(tmp_path):
    dest = _write_records(tmp_path)
    assert max_value(str(dest), "score") == 100


def test_field_stats_count(tmp_path):
    dest = _write_records(tmp_path)
    stats = field_stats(str(dest), "score")
    assert stats["count"] == 5


def test_field_stats_mean(tmp_path):
    dest = _write_records(tmp_path)
    stats = field_stats(str(dest), "score")
    assert stats["mean"] == 80.0
