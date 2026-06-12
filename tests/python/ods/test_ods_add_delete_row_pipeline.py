"""
test_ods_add_delete_row_pipeline.py -- ODS add_row + delete_row pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-83
Tests add_row increases row count, delete_row decreases row count,
add_row returns True, delete_row returns True, add then delete restores count.
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
    add_row,
    delete_row,
    get_row_count,
    write_ods,
    parse_ods_strict,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Sheet1")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="3"), OdsCell(value="4")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return doc, dest


def test_add_row_increases_count(tmp_path):
    doc, dest = _make_doc(tmp_path)
    before = len(doc.sheets[0].rows)
    ok, _ = add_row(doc, 0, ["X", "Y"])
    assert len(doc.sheets[0].rows) == before + 1


def test_delete_row_decreases_count(tmp_path):
    doc, dest = _make_doc(tmp_path)
    before = len(doc.sheets[0].rows)
    ok, _ = delete_row(doc, 0, 2)
    assert len(doc.sheets[0].rows) == before - 1


def test_add_row_returns_true(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, _ = add_row(doc, 0, ["P", "Q"])
    assert ok is True


def test_delete_row_returns_true(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, _ = delete_row(doc, 0, 1)
    assert ok is True


def test_add_then_delete_restores_count(tmp_path):
    doc, dest = _make_doc(tmp_path)
    original = len(doc.sheets[0].rows)
    add_row(doc, 0, ["Z", "W"])
    delete_row(doc, 0, original)
    assert len(doc.sheets[0].rows) == original
