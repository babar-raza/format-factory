"""
test_ndjson_flatten_unique_w115_pipeline.py -- NDJSON flatten_records + count_unique_values pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-115
Tests flatten_records returns list, expands nested dict, removes nested key,
count_unique_values returns int, correct unique count for dept field.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    flatten_records,
    count_unique_values,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "scores": {"q1": 90, "q2": 85}},
    {"name": "Bob", "dept": "hr", "scores": {"q1": 70, "q2": 75}},
    {"name": "Carol", "dept": "eng", "scores": {"q1": 80, "q2": 88}},
]


def test_flatten_records_returns_list():
    result = flatten_records(_RECORDS)
    assert isinstance(result, list)


def test_flatten_records_expands_nested():
    result = flatten_records(_RECORDS)
    assert "scores_q1" in result[0]


def test_flatten_records_removes_nested_key():
    result = flatten_records(_RECORDS)
    assert "scores" not in result[0]


def test_count_unique_values_returns_int():
    result = count_unique_values(_RECORDS, "dept")
    assert isinstance(result, int)


def test_count_unique_values_correct():
    result = count_unique_values(_RECORDS, "dept")
    assert result == 2
