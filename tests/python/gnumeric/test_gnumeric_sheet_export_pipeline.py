"""
test_gnumeric_sheet_export_pipeline.py -- Gnumeric sheet export pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-56
Tests export_to_csv has content, get_sheet_metadata list, extract_values list,
get_cell_count int, get_sheet_count int.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    get_sheet_metadata,
    extract_values,
    get_cell_count,
    get_sheet_count,
)

_SHEETS = [{"name": "Report", "rows": [
    ["Name", "Value"],
    ["Alpha", "10"],
    ["Beta", "20"],
]}]


def _write(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "book.gnumeric"
    write_gnumeric(model, str(dest))
    return dest


def test_export_to_csv_has_content(tmp_path):
    dest = _write(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Name" in csv_str
    assert "Alpha" in csv_str


def test_get_sheet_metadata_list(tmp_path):
    dest = _write(tmp_path)
    meta = get_sheet_metadata(str(dest))
    assert isinstance(meta, list)
    assert len(meta) >= 1


def test_extract_values_has_values(tmp_path):
    dest = _write(tmp_path)
    vals = extract_values(str(dest))
    assert isinstance(vals, list)
    assert "Name" in vals


def test_get_cell_count_int(tmp_path):
    dest = _write(tmp_path)
    count = get_cell_count(str(dest))
    assert isinstance(count, int)
    assert count >= 6


def test_get_sheet_count_one(tmp_path):
    dest = _write(tmp_path)
    count = get_sheet_count(str(dest))
    assert count == 1
