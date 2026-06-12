"""
test_ndjson_sort_pick_ops_pipeline.py -- NDJSON sort_by + pick pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-78
Tests sort_by ascending, sort_by descending first, pick extracts fields,
pick result count, zip_records combines lists.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    sort_by,
    pick,
    zip_records,
)

_RECORDS = [
    {"id": 3, "name": "Carol", "score": 90},
    {"id": 1, "name": "Alice", "score": 80},
    {"id": 2, "name": "Bob", "score": 70},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_sort_by_ascending():
    result = sort_by(_SOURCE, "score")
    assert result[0]["score"] == 70
    assert result[-1]["score"] == 90


def test_sort_by_descending_first():
    result = sort_by(_SOURCE, "score", reverse=True)
    assert result[0]["score"] == 90


def test_pick_extracts_fields():
    result = pick(_SOURCE, ["id", "name"])
    assert isinstance(result, list)
    assert "score" not in result[0]
    assert "name" in result[0]


def test_pick_result_count():
    result = pick(_SOURCE, ["name"])
    assert len(result) == 3


def test_zip_records_combines():
    list1 = [{"a": 1}, {"a": 2}]
    list2 = [{"b": 10}, {"b": 20}]
    result = zip_records(list1, list2)
    assert len(result) == 2
    assert result[0]["a"] == 1
    assert result[0]["b"] == 10
