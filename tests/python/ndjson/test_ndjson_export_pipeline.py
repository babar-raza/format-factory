"""
test_ndjson_export_pipeline.py -- NDJSON export and rename pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-45
Tests export_to_csv contains fields, write_csv creates file, rename_field renames,
pick selects fields, aggregate sum.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    export_to_csv,
    write_csv,
    rename_field,
    pick,
    aggregate,
    to_jsonl_str,
)

_RECORDS = [
    {"id": 1, "product": "Widget", "revenue": 1000},
    {"id": 2, "product": "Gadget", "revenue": 2000},
    {"id": 3, "product": "Doohickey", "revenue": 1500},
]


def _write(tmp_path):
    path = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(path))
    return path


def test_export_to_csv_has_header(tmp_path):
    src = _write(tmp_path)
    csv_str = export_to_csv(str(src))
    assert "product" in csv_str
    assert "Widget" in csv_str


def test_write_csv_creates_file(tmp_path):
    src = _write(tmp_path)
    dest = tmp_path / "out.csv"
    write_csv(str(src), str(dest))
    assert dest.exists()


def test_rename_field_renames(tmp_path):
    src = _write(tmp_path)
    result = rename_field(str(src), "revenue", "sales")
    assert result[0]["sales"] == 1000
    assert "revenue" not in result[0]


def test_pick_selects_fields(tmp_path):
    src = _write(tmp_path)
    result = pick(str(src), ["product", "revenue"])
    assert list(result[0].keys()) == ["product", "revenue"]


def test_aggregate_sum_revenue(tmp_path):
    src = _write(tmp_path)
    total = aggregate(str(src), "revenue", "sum")
    assert total == 4500
