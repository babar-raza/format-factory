"""
test_ods_avg_col_count_pipeline.py -- ODS average_column + get_column_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-89
Tests average_column float, average_column correct value, get_column_count int,
get_column_count=2, average_column second sheet.
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
    average_column,
    get_column_count,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Sheet1")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Item"), OdsCell(value="Val")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value=10.0, value_type="float")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="B"), OdsCell(value=20.0, value_type="float")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="C"), OdsCell(value=30.0, value_type="float")]))
    sheet2 = OdsSheet(name="Sheet2")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="X"), OdsCell(value="Y"), OdsCell(value="Z")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_average_column_float(tmp_path):
    dest = _make_doc(tmp_path)
    avg = average_column(str(dest), col=1)
    assert isinstance(avg, float)


def test_average_column_correct_value(tmp_path):
    dest = _make_doc(tmp_path)
    avg = average_column(str(dest), col=1)
    assert avg == 20.0


def test_get_column_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_column_count(str(dest))
    assert isinstance(count, int)


def test_get_column_count_value(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_column_count(str(dest))
    assert count == 2


def test_get_column_count_second_sheet(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_column_count(str(dest), sheet_index=1)
    assert count == 3
