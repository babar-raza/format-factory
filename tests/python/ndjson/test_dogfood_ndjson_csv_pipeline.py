"""
test_dogfood_ndjson_csv_pipeline.py -- NDJSON->CSV cross-format dogfood.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-7
Tests the full NDJSON->CSV export pipeline with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    export_to_csv,
)


_RECORDS = [
    {"name": "Alice", "score": 90},
    {"name": "Bob", "score": 75},
    {"name": "Carol", "score": 85},
]


def _make_src(tmp_path, records=None):
    if records is None:
        records = _RECORDS
    p = tmp_path / "data.ndjson"
    p.write_bytes(to_jsonl_str(records).encode())
    return p


def test_ndjson_csv_has_correct_header(tmp_path):
    src = _make_src(tmp_path)
    csv_str = export_to_csv(src)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) >= 2
    header = lines[0]
    assert "name" in header
    assert "score" in header


def test_ndjson_csv_row_count(tmp_path):
    src = _make_src(tmp_path)
    csv_str = export_to_csv(src)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    # header + 3 data rows
    assert len(lines) == 4


def test_ndjson_csv_contains_values(tmp_path):
    src = _make_src(tmp_path)
    csv_str = export_to_csv(src)
    assert "Alice" in csv_str
    assert "Bob" in csv_str
    assert "90" in csv_str


def test_ndjson_csv_single_record(tmp_path):
    src = _make_src(tmp_path, [{"x": 1, "y": 2}])
    csv_str = export_to_csv(src)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) == 2
