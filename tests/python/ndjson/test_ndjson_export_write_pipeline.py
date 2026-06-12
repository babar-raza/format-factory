"""
test_ndjson_export_write_pipeline.py -- NDJSON export_to_csv + write_ndjson pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-81
Tests write_ndjson creates file, export_to_csv returns string with data,
export_to_csv has header, load_ndjson after write count=3, count_records int.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    export_to_csv,
    load_ndjson,
    count_records,
    to_jsonl_str,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 85},
    {"name": "Bob", "dept": "hr", "score": 72},
    {"name": "Carol", "dept": "eng", "score": 91},
]


def test_write_ndjson_creates_file(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    assert dest.exists()


def test_export_to_csv_returns_string(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    csv_str = export_to_csv(str(dest))
    assert isinstance(csv_str, str)
    assert "Alice" in csv_str


def test_export_to_csv_has_header(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    csv_str = export_to_csv(str(dest))
    assert "name" in csv_str


def test_load_ndjson_after_write_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    records = load_ndjson(str(dest))
    assert len(records) == 3


def test_count_records_int(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    count = count_records(str(dest))
    assert isinstance(count, int)
    assert count == 3
