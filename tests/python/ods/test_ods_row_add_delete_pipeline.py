"""
test_ods_row_add_delete_pipeline.py -- ODS row add/delete pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-59
Tests add_row success, add_row increases row count, delete_row success,
delete_row decreases count, get_row_values after add.
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
    get_row_count,
    get_row_values,
    add_row,
    delete_row,
)


def _make_doc():
    sheet = OdsSheet(name="Sheet1")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    return OdsDocument(sheets=[sheet])


def test_add_row_success():
    doc = _make_doc()
    ok, msg = add_row(doc, 0, ["X", "Y"])
    assert ok is True


def test_add_row_increases_count(tmp_path):
    doc = _make_doc()
    add_row(doc, 0, ["X", "Y"])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    count = get_row_count(str(dest), sheet_index=0)
    assert count == 3


def test_delete_row_success():
    doc = _make_doc()
    ok, msg = delete_row(doc, 0, 0)
    assert ok is True


def test_delete_row_decreases_count(tmp_path):
    doc = _make_doc()
    delete_row(doc, 0, 1)
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    count = get_row_count(str(dest), sheet_index=0)
    assert count == 1


def test_get_row_values_after_add(tmp_path):
    doc = _make_doc()
    add_row(doc, 0, ["NewVal", "42"])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    vals = get_row_values(str(dest), sheet_index=0, row=2)
    assert "NewVal" in vals
