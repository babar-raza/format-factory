"""
test_ods_multisheet_filter_pipeline.py -- ODS multisheet filter pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-71
Tests get_column_values list, filter_rows_by_value returns list,
filter_rows_by_value correct count, sum_column float, column values sheet1.
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
    get_column_values,
    filter_rows_by_value,
    sum_column,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Sales")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Region"), OdsCell(value="Amount")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="North"), OdsCell(value=100.0, value_type="float")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="South"), OdsCell(value=200.0, value_type="float")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="North"), OdsCell(value=150.0, value_type="float")]))
    sheet2 = OdsSheet(name="Targets")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Region"), OdsCell(value="Target")]))
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="North"), OdsCell(value=300.0, value_type="float")]))
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="South"), OdsCell(value=400.0, value_type="float")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "sales.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_column_values_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    result = get_column_values(str(dest), col=0)
    assert isinstance(result, list)
    assert len(result) == 4


def test_filter_rows_by_value_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    result = filter_rows_by_value(str(dest), col=0, value="North")
    assert isinstance(result, list)


def test_filter_rows_by_value_correct_count(tmp_path):
    dest = _make_doc(tmp_path)
    result = filter_rows_by_value(str(dest), col=0, value="North")
    assert len(result) == 2


def test_sum_column_float(tmp_path):
    dest = _make_doc(tmp_path)
    total = sum_column(str(dest), col=1)
    assert isinstance(total, float)
    assert total == 450.0


def test_get_column_values_sheet1(tmp_path):
    dest = _make_doc(tmp_path)
    result = get_column_values(str(dest), col=1, sheet_index=1)
    assert isinstance(result, list)
    assert len(result) == 3
