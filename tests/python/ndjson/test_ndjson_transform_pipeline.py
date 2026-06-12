"""
test_ndjson_transform_pipeline.py -- NDJSON field transformation pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-20
Tests chained NDJSON operations: rename_field, filter, pick, head, sum_field
with write_ndjson+reload roundtrip to verify persistence.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    load_ndjson,
    write_ndjson,
    to_jsonl_str,
    rename_field,
    filter_records,
    pick,
    head,
    sum_field,
    get_record_count,
)

_RECORDS = [
    {"name": "Alice", "score": 90, "dept": "eng"},
    {"name": "Bob", "score": 75, "dept": "mkt"},
    {"name": "Carol", "score": 85, "dept": "eng"},
    {"name": "Dave", "score": 60, "dept": "mkt"},
]
_SOURCE = (to_jsonl_str(_RECORDS) + "\n").encode()


def test_rename_field_write_reload(tmp_path):
    renamed = rename_field(_SOURCE, "score", "points")
    dest = tmp_path / "renamed.ndjson"
    write_ndjson(renamed, str(dest))
    reloaded = load_ndjson(str(dest))
    assert all("points" in r for r in reloaded)
    assert all("score" not in r for r in reloaded)


def test_filter_write_reload_count(tmp_path):
    eng_records = filter_records(_SOURCE, "dept", "eng")
    dest = tmp_path / "eng.ndjson"
    write_ndjson(eng_records, str(dest))
    count = get_record_count(str(dest))
    assert count == 2


def test_pick_write_reload_fields(tmp_path):
    picked = pick(_SOURCE, ["name", "score"])
    dest = tmp_path / "picked.ndjson"
    write_ndjson(picked, str(dest))
    reloaded = load_ndjson(str(dest))
    assert all("name" in r and "score" in r for r in reloaded)
    assert all("dept" not in r for r in reloaded)


def test_head_write_reload_count(tmp_path):
    top2 = head(_SOURCE, 2)
    dest = tmp_path / "top2.ndjson"
    write_ndjson(top2, str(dest))
    count = get_record_count(str(dest))
    assert count == 2


def test_sum_field_after_filter(tmp_path):
    eng_records = filter_records(_SOURCE, "dept", "eng")
    eng_bytes = (to_jsonl_str(eng_records) + "\n").encode()
    total = sum_field(eng_bytes, "score")
    assert total == 175.0
