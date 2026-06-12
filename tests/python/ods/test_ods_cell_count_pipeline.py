"""
test_ods_cell_count_pipeline.py -- ODS cell count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-65
Tests get_cell_count int, count_sheets, get_column_count, get_row_count, ods_to_csv string.
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
    get_cell_count,
    count_sheets,
    get_column_count,
    get_row_count,
    ods_to_csv,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Sheet1")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B"), OdsCell(value="C")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2"), OdsCell(value="3")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="4"), OdsCell(value="5"), OdsCell(value="6")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_cell_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_cell_count(str(dest), sheet_index=0)
    assert isinstance(count, int)
    assert count == 9


def test_count_sheets(tmp_path):
    dest = _make_doc(tmp_path)
    assert count_sheets(str(dest)) == 1


def test_get_column_count(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_column_count(str(dest), sheet_index=0)
    assert count == 3


def test_get_row_count(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_row_count(str(dest), sheet_index=0)
    assert count == 3


def test_ods_to_csv_string(tmp_path):
    dest = _make_doc(tmp_path)
    csv_str = ods_to_csv(str(dest), sheet_index=0)
    assert isinstance(csv_str, str)
    assert "A" in csv_str
