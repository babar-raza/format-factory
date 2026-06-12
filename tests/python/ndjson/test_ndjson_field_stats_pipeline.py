"""
test_ndjson_field_stats_pipeline.py -- NDJSON field stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-72
Tests field_stats returns dict, field_stats has min/max, distinct_values list,
filter_records returns list, get_field_names returns expected key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    field_stats,
    distinct_values,
    filter_records,
    get_field_names,
)

_RECORDS = [
    {"id": 1, "dept": "eng", "score": 80},
    {"id": 2, "dept": "hr", "score": 60},
    {"id": 3, "dept": "eng", "score": 90},
    {"id": 4, "dept": "mkt", "score": 70},
    {"id": 5, "dept": "eng", "score": 75},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_field_stats_returns_dict():
    result = field_stats(_SOURCE, "score")
    assert isinstance(result, dict)


def test_field_stats_has_min_max():
    result = field_stats(_SOURCE, "score")
    assert "min" in result
    assert "max" in result
    assert result["min"] == 60
    assert result["max"] == 90


def test_distinct_values_returns_list():
    result = distinct_values(_SOURCE, "dept")
    assert isinstance(result, list)
    assert len(result) == 3


def test_filter_records_returns_list():
    result = filter_records(_SOURCE, "dept", "eng")
    assert isinstance(result, list)
    assert len(result) == 3


def test_get_field_names_has_key():
    result = get_field_names(_SOURCE)
    assert isinstance(result, list)
    assert "dept" in result
    assert "score" in result
