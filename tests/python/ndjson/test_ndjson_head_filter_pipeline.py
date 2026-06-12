"""
test_ndjson_head_filter_pipeline.py -- NDJSON head + filter_records pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-99
Tests head returns list, head count=2, filter_records returns list, filter finds eng dept,
filter returns empty for no match.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    head,
    filter_records,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 90},
    {"name": "Bob", "dept": "hr", "score": 75},
    {"name": "Carol", "dept": "eng", "score": 85},
    {"name": "Dave", "dept": "hr", "score": 70},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_head_returns_list():
    result = head(_SOURCE, 2)
    assert isinstance(result, list)


def test_head_correct_count():
    result = head(_SOURCE, 2)
    assert len(result) == 2


def test_filter_records_returns_list():
    result = filter_records(_SOURCE, "dept", "eng")
    assert isinstance(result, list)


def test_filter_records_finds_correct():
    result = filter_records(_SOURCE, "dept", "eng")
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Carol" in names
    assert len(result) == 2


def test_filter_records_empty_no_match():
    result = filter_records(_SOURCE, "dept", "finance")
    assert result == []
