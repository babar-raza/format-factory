"""
test_ods_multisheet_aggregation.py -- ODS multi-sheet aggregation tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-27
Tests get_sheet_names, count_sheets, get_row_values, get_all_values,
get_cell_count on a two-sheet ODS document.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    get_sheet_names,
    count_sheets,
    get_row_values,
    get_all_values,
    get_cell_count,
)
from ods.ods_writer import write_ods


def _make_two_sheet_doc(tmp_path):
    sheet1 = OdsSheet(name="Sales")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Product"), OdsCell(value="Revenue")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Widget"), OdsCell(value=500.0, value_type="float")]))
    sheet2 = OdsSheet(name="Costs")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Item"), OdsCell(value="Cost")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "two_sheets.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_sheet_names(tmp_path):
    dest = _make_two_sheet_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Sales" in names
    assert "Costs" in names


def test_count_sheets(tmp_path):
    dest = _make_two_sheet_doc(tmp_path)
    assert count_sheets(str(dest)) == 2


def test_get_row_values_header(tmp_path):
    dest = _make_two_sheet_doc(tmp_path)
    row = get_row_values(str(dest), sheet_index=0, row=0)
    assert "Product" in row


def test_get_all_values_sales(tmp_path):
    dest = _make_two_sheet_doc(tmp_path)
    values = get_all_values(str(dest), sheet_index=0)
    assert "Widget" in values


def test_get_cell_count_sales(tmp_path):
    dest = _make_two_sheet_doc(tmp_path)
    count = get_cell_count(str(dest), sheet_index=0)
    assert count == 4  # 2 rows x 2 cols
