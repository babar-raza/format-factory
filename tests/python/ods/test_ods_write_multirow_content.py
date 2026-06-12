"""
test_ods_write_multirow_content.py -- ODS write multi-row and reload content verification.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-25
Tests that a manually constructed ODS document with multiple rows per sheet
writes correctly and all cell values are retrievable after reload.
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
    get_cell_value,
    get_row_count,
    get_column_count,
)
from ods.ods_writer import write_ods


def _make_three_row_doc():
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value=90.0, value_type="float")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value=75.0, value_type="float")]))
    return OdsDocument(sheets=[sheet])


def test_three_row_write_reload_row_count(tmp_path):
    doc = _make_three_row_doc()
    dest = tmp_path / "three_rows.ods"
    write_ods(doc, str(dest))
    assert get_row_count(str(dest)) == 3


def test_three_row_write_reload_col_count(tmp_path):
    doc = _make_three_row_doc()
    dest = tmp_path / "three_rows.ods"
    write_ods(doc, str(dest))
    assert get_column_count(str(dest)) == 2


def test_header_row_name_cell(tmp_path):
    doc = _make_three_row_doc()
    dest = tmp_path / "three_rows.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val == "Name"


def test_data_row_alice(tmp_path):
    doc = _make_three_row_doc()
    dest = tmp_path / "three_rows.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=1, col=0)
    assert val == "Alice"


def test_data_row_bob_score(tmp_path):
    doc = _make_three_row_doc()
    dest = tmp_path / "three_rows.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=2, col=1)
    assert val == 75.0
