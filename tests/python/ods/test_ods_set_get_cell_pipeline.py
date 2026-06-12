"""
test_ods_set_get_cell_pipeline.py -- ODS set_cell_value + get_cell_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-107
Tests set_cell_value returns True, value updated in file, get_cell_value returns correct value,
set then get roundtrip, original value before set matches expected.
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
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="eng")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="hr")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return doc, dest


def test_get_cell_value_original(tmp_path):
    doc, dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), 0, 0, 0)
    assert val == "Alice"


def test_set_cell_value_returns_true(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, _ = set_cell_value(doc, 0, 0, 0, "Updated")
    assert ok is True


def test_set_cell_value_updates_file(tmp_path):
    doc, dest = _make_doc(tmp_path)
    set_cell_value(doc, 0, 0, 0, "Updated")
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), 0, 0, 0)
    assert val == "Updated"


def test_set_get_roundtrip(tmp_path):
    doc, dest = _make_doc(tmp_path)
    set_cell_value(doc, 0, 1, 1, "finance")
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), 0, 1, 1)
    assert val == "finance"


def test_get_cell_value_second_row(tmp_path):
    doc, dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), 0, 1, 0)
    assert val == "Bob"
