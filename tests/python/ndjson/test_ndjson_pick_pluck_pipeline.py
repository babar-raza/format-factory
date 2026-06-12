"""
test_ndjson_pick_pluck_pipeline.py -- NDJSON pick + pluck pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-105
Tests pick returns list of dicts, only requested fields kept, pluck returns list,
pluck values are names, pluck count=4.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    pick,
    pluck,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 90},
    {"name": "Bob", "dept": "hr", "score": 75},
    {"name": "Carol", "dept": "eng", "score": 85},
    {"name": "Dave", "dept": "hr", "score": 65},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_pick_returns_list():
    result = pick(_SOURCE, ["name", "dept"])
    assert isinstance(result, list)


def test_pick_only_requested_fields():
    result = pick(_SOURCE, ["name"])
    for rec in result:
        assert set(rec.keys()) == {"name"}


def test_pluck_returns_list():
    result = pluck(_SOURCE, "name")
    assert isinstance(result, list)


def test_pluck_has_expected_names():
    result = pluck(_SOURCE, "name")
    assert "Alice" in result
    assert "Carol" in result


def test_pluck_count():
    result = pluck(_SOURCE, "name")
    assert len(result) == 4
