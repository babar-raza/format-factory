"""
test_ods_set_cell_roundtrip_pipeline.py -- ODS set_cell_value + roundtrip pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-53
Tests set_cell_value success, set then write then read, get_all_values has new value,
ods_to_csv has updated value, get_column_values after set.
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
    set_cell_value,
    get_cell_value,
    get_all_values,
    ods_to_csv,
    get_column_values,
)


def _make_doc():
    sheet = OdsSheet(name="Sheet1")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    return OdsDocument(sheets=[sheet])


def test_set_cell_value_success():
    doc = _make_doc()
    ok, msg = set_cell_value(doc, 0, 0, 0, "Updated")
    assert ok is True


def test_set_then_write_then_read(tmp_path):
    doc = _make_doc()
    set_cell_value(doc, 0, 1, 0, "NewVal")
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), sheet_index=0, row=1, col=0)
    assert val == "NewVal"


def test_get_all_values_has_updated(tmp_path):
    doc = _make_doc()
    set_cell_value(doc, 0, 0, 0, "X-Updated")
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    vals = get_all_values(str(dest), sheet_index=0)
    assert "X-Updated" in vals


def test_ods_to_csv_has_updated_value(tmp_path):
    doc = _make_doc()
    set_cell_value(doc, 0, 0, 1, "B-Updated")
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    csv_str = ods_to_csv(str(dest), sheet_index=0)
    assert "B-Updated" in csv_str


def test_get_column_values_after_set(tmp_path):
    doc = _make_doc()
    set_cell_value(doc, 0, 1, 0, "Row2Col0")
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    col_vals = get_column_values(str(dest), col=0, sheet_index=0)
    assert "Row2Col0" in col_vals
