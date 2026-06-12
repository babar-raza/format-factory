"""
test_ods_set_cell_rename_pipeline.py -- ODS set_cell + rename_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-74
Tests set_cell_value changes cell, rename_sheet changes name, add_sheet increases
count, remove_sheet decreases count, get_cell_value after set.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    write_ods,
    parse_ods_strict,
    count_sheets,
    get_cell_value,
    set_cell_value,
    rename_sheet,
    add_sheet,
    remove_sheet,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Main")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_set_cell_value_changes_cell(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    updated, msg = set_cell_value(doc, sheet_index=0, row=0, col=0, value="Updated")
    assert updated is True
    assert doc.sheets[0].rows[0].cells[0].value == "Updated"


def test_rename_sheet_changes_name(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    success, msg = rename_sheet(doc, "Main", "Renamed")
    assert success is True
    assert doc.sheets[0].name == "Renamed"


def test_add_sheet_increases_count(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    before = len(doc.sheets)
    add_sheet(doc, "New")
    assert len(doc.sheets) == before + 1


def test_remove_sheet_decreases_count(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    add_sheet(doc, "Extra")
    before = len(doc.sheets)
    remove_sheet(doc, "Extra")
    assert len(doc.sheets) == before - 1


def test_get_cell_value_after_set(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    set_cell_value(doc, sheet_index=0, row=1, col=1, value="99")
    assert doc.sheets[0].rows[1].cells[1].value == "99"
