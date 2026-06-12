"""
test_ndjson_sort_pick_pipeline.py -- NDJSON sort+pick+write pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-25
Tests chaining sort_by, pick, write_ndjson and verifying result order/fields.
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
    write_ndjson,
    load_ndjson,
    pluck,
    tail,
)

_RECORDS = [
    {"name": "Dave", "score": 60, "dept": "mkt"},
    {"name": "Alice", "score": 90, "dept": "eng"},
    {"name": "Carol", "score": 85, "dept": "eng"},
    {"name": "Bob", "score": 75, "dept": "mkt"},
]
_SOURCE = (to_jsonl_str(_RECORDS) + "\n").encode()


def test_sort_by_name_ascending():
    sorted_recs = sort_by(_SOURCE, "name")
    assert sorted_recs[0]["name"] == "Alice"
    assert sorted_recs[-1]["name"] == "Dave"


def test_sort_by_score_descending():
    sorted_recs = sort_by(_SOURCE, "score", reverse=True)
    assert sorted_recs[0]["score"] == 90
    assert sorted_recs[-1]["score"] == 60


def test_pick_then_write_reload(tmp_path):
    picked = pick(_SOURCE, ["name", "score"])
    dest = tmp_path / "picked.ndjson"
    write_ndjson(picked, str(dest))
    reloaded = load_ndjson(str(dest))
    assert all("name" in r and "score" in r for r in reloaded)
    assert all("dept" not in r for r in reloaded)


def test_pluck_names():
    names = pluck(_SOURCE, "name")
    assert set(names) == {"Alice", "Bob", "Carol", "Dave"}


def test_tail_two_records(tmp_path):
    last2 = tail(_SOURCE, 2)
    assert len(last2) == 2
    assert last2[-1]["name"] == "Bob"
