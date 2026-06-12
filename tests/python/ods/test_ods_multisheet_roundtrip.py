"""
test_ods_multisheet_roundtrip.py -- ODS multi-sheet creation and access roundtrip.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-21
Tests creating ODS documents with multiple sheets, writing, and reloading
to verify each sheet's name and cell content are preserved.
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
    parse_ods_strict,
    get_sheet_names,
    count_sheets,
    get_cell_value,
)
from ods.ods_writer import write_ods


def _make_two_sheet_doc():
    sheet1 = OdsSheet(name="Numbers")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))

    sheet2 = OdsSheet(name="Names")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Alice")]))
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Bob")]))

    return OdsDocument(sheets=[sheet1, sheet2])


def test_two_sheet_write_reload_count(tmp_path):
    doc = _make_two_sheet_doc()
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    assert count_sheets(str(dest)) == 2


def test_two_sheet_write_reload_names(tmp_path):
    doc = _make_two_sheet_doc()
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    names = get_sheet_names(str(dest))
    assert "Numbers" in names
    assert "Names" in names


def test_first_sheet_cell_value(tmp_path):
    doc = _make_two_sheet_doc()
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val == "A"


def test_second_sheet_cell_value(tmp_path):
    doc = _make_two_sheet_doc()
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=1, row=0, col=0)
    assert val == "Alice"


def test_second_sheet_second_row(tmp_path):
    doc = _make_two_sheet_doc()
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=1, row=1, col=0)
    assert val == "Bob"
