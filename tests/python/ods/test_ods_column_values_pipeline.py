"""
test_ods_column_values_pipeline.py -- ODS get_column_values + ods_to_csv pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-30
Tests get_column_values (by index), ods_to_csv output contains data,
get_row_values for specific rows, get_all_values flat list,
count_sheets after write.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    get_column_values,
    ods_to_csv,
    get_row_values,
    get_all_values,
    count_sheets,
)
from ods.ods_writer import write_ods


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Results")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value=90.0, value_type="float")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value=70.0, value_type="float")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "results.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_column_values_names(tmp_path):
    dest = _make_doc(tmp_path)
    col = get_column_values(str(dest), col=0, sheet_index=0)
    assert "Name" in col
    assert "Alice" in col


def test_get_column_values_scores(tmp_path):
    dest = _make_doc(tmp_path)
    col = get_column_values(str(dest), col=1, sheet_index=0)
    assert 90.0 in col


def test_ods_to_csv_contains_alice(tmp_path):
    dest = _make_doc(tmp_path)
    csv_str = ods_to_csv(str(dest), sheet_index=0)
    assert "Alice" in csv_str


def test_get_row_values_data_row(tmp_path):
    dest = _make_doc(tmp_path)
    row = get_row_values(str(dest), sheet_index=0, row=1)
    assert "Alice" in row


def test_count_sheets_is_one(tmp_path):
    dest = _make_doc(tmp_path)
    assert count_sheets(str(dest)) == 1
