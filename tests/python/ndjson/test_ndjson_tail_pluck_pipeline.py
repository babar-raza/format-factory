"""
test_ndjson_tail_pluck_pipeline.py -- NDJSON tail + pluck pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-54
Tests tail returns last N, tail count, pluck extracts field, pluck list,
tail then pluck combined.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    tail,
    pluck,
)

_RECORDS = [
    {"id": 1, "name": "Alice", "dept": "eng"},
    {"id": 2, "name": "Bob", "dept": "mkt"},
    {"id": 3, "name": "Carol", "dept": "eng"},
    {"id": 4, "name": "Dave", "dept": "hr"},
    {"id": 5, "name": "Eve", "dept": "eng"},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_tail_returns_list():
    result = tail(_SOURCE, 3)
    assert isinstance(result, list)


def test_tail_count():
    result = tail(_SOURCE, 3)
    assert len(result) == 3


def test_tail_last_record():
    result = tail(_SOURCE, 1)
    assert result[0]["name"] == "Eve"


def test_pluck_extracts_field():
    result = pluck(_SOURCE, "name")
    assert "Alice" in result
    assert "Eve" in result


def test_tail_then_pluck():
    last_two = tail(_SOURCE, 2)
    src2 = to_jsonl_str(last_two).encode()
    names = pluck(src2, "name")
    assert names == ["Dave", "Eve"]
