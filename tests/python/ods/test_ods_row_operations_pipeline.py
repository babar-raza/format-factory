"""
test_ods_row_operations_pipeline.py -- ODS row operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-47
Tests add_row increases row_count, delete_row decreases count,
set_cell_value + get_cell_value, get_row_values after add_row,
get_column_count after write.
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
    add_row,
    delete_row,
    set_cell_value,
    get_cell_value,
    get_row_count,
    get_row_values,
    get_column_count,
)


def _make_doc():
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    return OdsDocument(sheets=[sheet])


def test_add_row_increases_count(tmp_path):
    doc = _make_doc()
    add_row(doc, 0, ["X", "Y"])
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    assert get_row_count(str(dest), sheet_index=0) == 3


def test_delete_row_decreases_count(tmp_path):
    doc = _make_doc()
    delete_row(doc, 0, 1)
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    assert get_row_count(str(dest), sheet_index=0) == 1


def test_set_cell_value_readable(tmp_path):
    doc = _make_doc()
    set_cell_value(doc, 0, 0, 0, "Updated")
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val == "Updated"


def test_get_row_values_after_add_row(tmp_path):
    doc = _make_doc()
    add_row(doc, 0, ["New1", "New2"])
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    row_vals = get_row_values(str(dest), sheet_index=0, row=2)
    assert "New1" in row_vals


def test_get_column_count(tmp_path):
    doc = _make_doc()
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    assert get_column_count(str(dest), sheet_index=0) == 2
