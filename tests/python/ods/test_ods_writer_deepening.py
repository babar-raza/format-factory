"""
test_ods_writer_deepening.py -- ODS writer operations deepening.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-11
Tests set_cell_value, add_row, delete_row, add_sheet, rename_sheet
using OdsDocument from parse_ods_strict with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import parse_ods_strict
from ods.ods_writer import (
    set_cell_value,
    add_row,
    delete_row,
    add_sheet,
    rename_sheet,
)


def test_set_cell_value_returns_success():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    ok, msg = set_cell_value(doc, 0, 0, 0, "hello")
    assert ok is True


def test_set_cell_value_persists_in_model():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    set_cell_value(doc, 0, 0, 0, "updated_value")
    assert doc.sheets[0].rows[0].cells[0].text == "updated_value"


def test_add_row_increases_row_count():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    before = len(doc.sheets[0].rows)
    add_row(doc, 0, ["A", "B", "C"])
    assert len(doc.sheets[0].rows) == before + 1


def test_add_row_values_correct():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    add_row(doc, 0, ["X", "Y", "Z"])
    last_row = doc.sheets[0].rows[-1]
    assert last_row.cells[0].text == "X"
    assert last_row.cells[2].text == "Z"


def test_delete_row_decreases_count():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    before = len(doc.sheets[0].rows)
    ok, _ = delete_row(doc, 0, 0)
    assert ok is True
    assert len(doc.sheets[0].rows) == before - 1


def test_add_sheet_creates_new_sheet():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    before = len(doc.sheets)
    ok, _ = add_sheet(doc, "NewSheet")
    assert ok is True
    assert len(doc.sheets) == before + 1
    assert doc.sheets[-1].name == "NewSheet"


def test_rename_sheet_updates_name():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    original_name = doc.sheets[0].name
    ok, _ = rename_sheet(doc, original_name, "RenamedSheet")
    assert ok is True
    assert doc.sheets[0].name == "RenamedSheet"
