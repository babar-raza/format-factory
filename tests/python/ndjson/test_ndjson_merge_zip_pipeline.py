"""
test_ndjson_merge_zip_pipeline.py -- NDJSON merge_ndjson + zip_records pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-87
Tests merge_ndjson returns list, merge count=4, zip_records returns list,
zip_records count matches, zip_records combines fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    merge_ndjson,
    zip_records,
)

_RECORDS_A = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]
_RECORDS_B = [
    {"id": 3, "name": "Carol"},
    {"id": 4, "name": "Dave"},
]


def test_merge_ndjson_returns_list(tmp_path):
    dest_a = tmp_path / "a.ndjson"
    dest_b = tmp_path / "b.ndjson"
    write_ndjson(_RECORDS_A, str(dest_a))
    write_ndjson(_RECORDS_B, str(dest_b))
    result = merge_ndjson(str(dest_a), str(dest_b))
    assert isinstance(result, list)


def test_merge_ndjson_count(tmp_path):
    dest_a = tmp_path / "a.ndjson"
    dest_b = tmp_path / "b.ndjson"
    write_ndjson(_RECORDS_A, str(dest_a))
    write_ndjson(_RECORDS_B, str(dest_b))
    result = merge_ndjson(str(dest_a), str(dest_b))
    assert len(result) == 4


def test_zip_records_returns_list(tmp_path):
    list1 = [{"x": 1}, {"x": 2}]
    list2 = [{"y": "a"}, {"y": "b"}]
    result = zip_records(list1, list2)
    assert isinstance(result, list)


def test_zip_records_count_matches(tmp_path):
    list1 = [{"x": 1}, {"x": 2}, {"x": 3}]
    list2 = [{"y": "a"}, {"y": "b"}, {"y": "c"}]
    result = zip_records(list1, list2)
    assert len(result) == 3


def test_zip_records_combines_fields(tmp_path):
    list1 = [{"x": 1}]
    list2 = [{"y": "a"}]
    result = zip_records(list1, list2)
    assert "x" in result[0]
    assert "y" in result[0]
