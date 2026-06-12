"""
test_ndjson_roundtrip_csv_pipeline.py -- NDJSON roundtrip + write_csv pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-34
Tests roundtrip (write+reload), write_csv produces file, export_to_csv string,
zip_records combines two lists, count_by returns dict.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    roundtrip,
    write_csv,
    export_to_csv,
    zip_records,
    count_by,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 90},
    {"name": "Bob", "dept": "mkt", "score": 70},
    {"name": "Carol", "dept": "eng", "score": 85},
]


def _write_src(tmp_path):
    src = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(src))
    return src


def test_roundtrip_reloads_records(tmp_path):
    src = _write_src(tmp_path)
    dest = tmp_path / "copy.ndjson"
    reloaded = roundtrip(str(src), str(dest))
    assert len(reloaded) == 3
    assert reloaded[0]["name"] == "Alice"


def test_write_csv_creates_file(tmp_path):
    src = _write_src(tmp_path)
    csv_dest = tmp_path / "out.csv"
    write_csv(str(src), str(csv_dest))
    assert csv_dest.exists()


def test_export_to_csv_contains_alice(tmp_path):
    src = _write_src(tmp_path)
    csv_str = export_to_csv(str(src))
    assert "Alice" in csv_str


def test_zip_records_combines():
    list1 = [{"a": 1}, {"a": 2}]
    list2 = [{"b": 10}, {"b": 20}]
    zipped = zip_records(list1, list2)
    assert zipped[0]["a"] == 1
    assert zipped[0]["b"] == 10


def test_count_by_dept(tmp_path):
    src = _write_src(tmp_path)
    counts = count_by(str(src), "dept")
    assert counts["eng"] == 2
    assert counts["mkt"] == 1
