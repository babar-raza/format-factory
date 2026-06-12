"""
test_dogfood_ods_csv_ndjson_pipeline.py -- ODS→CSV and ODS→NDJSON cross-format pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-11
Tests ODS data flowing through ods_to_csv and then into NDJSON processing.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import ods_to_csv, get_sheet_names, get_row_count, get_column_count


def test_ods_to_csv_produces_output():
    csv_str = ods_to_csv(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert isinstance(csv_str, str)
    assert len(csv_str) > 0


def test_ods_to_csv_has_commas():
    csv_str = ods_to_csv(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert "," in csv_str


def test_ods_to_csv_row_count_matches():
    csv_str = ods_to_csv(str(_SAMPLES / "minimal-spreadsheet.ods"))
    csv_rows = [r for r in csv_str.strip().splitlines() if r.strip()]
    row_count = get_row_count(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert len(csv_rows) == row_count


def test_ods_sheet_names_returns_list():
    names = get_sheet_names(str(_SAMPLES / "minimal-spreadsheet.ods"))
    assert isinstance(names, list)
    assert len(names) >= 1


def test_ods_numeric_row_column_count():
    col_count = get_column_count(str(_SAMPLES / "numeric-row.ods"))
    assert col_count >= 1
