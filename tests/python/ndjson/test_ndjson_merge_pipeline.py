"""
test_ndjson_merge_pipeline.py -- NDJSON merge_ndjson pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-31
Tests merge_ndjson: combined count, no duplicates from distinct sources,
merged write+reload, get_record_count after merge, distinct_values after merge.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    merge_ndjson,
    load_ndjson,
    get_record_count,
    distinct_values,
    to_jsonl_str,
)

_RECORDS_A = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "mkt"},
]
_RECORDS_B = [
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "hr"},
]


def _write_sources(tmp_path):
    src_a = tmp_path / "a.ndjson"
    src_b = tmp_path / "b.ndjson"
    write_ndjson(_RECORDS_A, str(src_a))
    write_ndjson(_RECORDS_B, str(src_b))
    return src_a, src_b


def test_merge_ndjson_combined_count(tmp_path):
    src_a, src_b = _write_sources(tmp_path)
    merged = merge_ndjson(str(src_a), str(src_b))
    assert len(merged) == 4


def test_merge_ndjson_contains_all_names(tmp_path):
    src_a, src_b = _write_sources(tmp_path)
    merged = merge_ndjson(str(src_a), str(src_b))
    names = [r["name"] for r in merged]
    assert "Alice" in names
    assert "Carol" in names


def test_merge_ndjson_write_reload(tmp_path):
    src_a, src_b = _write_sources(tmp_path)
    merged = merge_ndjson(str(src_a), str(src_b))
    dest = tmp_path / "merged.ndjson"
    write_ndjson(merged, str(dest))
    reloaded = load_ndjson(str(dest))
    assert len(reloaded) == 4


def test_get_record_count_after_merge(tmp_path):
    src_a, src_b = _write_sources(tmp_path)
    merged = merge_ndjson(str(src_a), str(src_b))
    dest = tmp_path / "merged.ndjson"
    write_ndjson(merged, str(dest))
    assert get_record_count(str(dest)) == 4


def test_distinct_values_after_merge(tmp_path):
    src_a, src_b = _write_sources(tmp_path)
    merged = merge_ndjson(str(src_a), str(src_b))
    dest = tmp_path / "merged.ndjson"
    write_ndjson(merged, str(dest))
    depts = distinct_values(str(dest), "dept")
    assert "eng" in depts
    assert "hr" in depts
