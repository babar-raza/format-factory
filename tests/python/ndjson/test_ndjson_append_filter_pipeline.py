"""
test_ndjson_append_filter_pipeline.py -- NDJSON append_record + filter pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-75
Tests append_record increases file count, filter_records returns matching list,
filter_records count, load_ndjson after append, count_records after append.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    append_record,
    load_ndjson,
    filter_records,
    count_records,
)

_INITIAL = [
    {"id": 1, "type": "A", "val": 10},
    {"id": 2, "type": "B", "val": 20},
    {"id": 3, "type": "A", "val": 30},
]


def test_append_record_increases_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_INITIAL, str(dest))
    append_record(str(dest), {"id": 4, "type": "C", "val": 40})
    result = load_ndjson(str(dest))
    assert len(result) == 4


def test_filter_records_returns_matching(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_INITIAL, str(dest))
    result = filter_records(str(dest), "type", "A")
    assert isinstance(result, list)


def test_filter_records_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_INITIAL, str(dest))
    result = filter_records(str(dest), "type", "A")
    assert len(result) == 2


def test_load_ndjson_after_append(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_INITIAL, str(dest))
    append_record(str(dest), {"id": 5, "type": "A", "val": 50})
    records = load_ndjson(str(dest))
    assert records[-1]["id"] == 5


def test_count_records_after_append(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_INITIAL, str(dest))
    append_record(str(dest), {"id": 6, "type": "B", "val": 60})
    total = count_records(str(dest))
    assert total == 4
