"""
test_ndjson_sort_pick_w120_pipeline.py -- NDJSON sort_records + pick pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-120
Tests sort_records returns list, records sorted ascending by score,
pick returns list, pick keeps only selected fields, pick has name field.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    sort_records,
    pick,
)

_RECORDS = [
    {"name": "Carol", "score": 80, "dept": "eng"},
    {"name": "Alice", "score": 95, "dept": "hr"},
    {"name": "Bob", "score": 70, "dept": "eng"},
]
_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_sort_records_returns_list():
    result = sort_records(_SOURCE, "score")
    assert isinstance(result, list)


def test_sort_records_ordered_ascending():
    result = sort_records(_SOURCE, "score")
    scores = [r["score"] for r in result]
    assert scores == sorted(scores)


def test_pick_returns_list():
    result = pick(_SOURCE, ["name", "score"])
    assert isinstance(result, list)


def test_pick_keeps_only_selected_fields():
    result = pick(_SOURCE, ["name", "score"])
    assert "dept" not in result[0]


def test_pick_has_name_field():
    result = pick(_SOURCE, ["name", "score"])
    assert "name" in result[0]
