"""
test_ods_row_values_sheet_order_pipeline.py -- ODS get_row_values + sheet_name_order pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-86
Tests get_row_values returns list, get_row_values header row, sheet_name_order returns list,
sheet_name_order has names, get_row_values data row.
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
    get_row_values,
    sheet_name_order,
    parse_ods,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Alpha")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="90")]))
    sheet2 = OdsSheet(name="Beta")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="X"), OdsCell(value="Y")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_row_values_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    row = get_row_values(str(dest), sheet_index=0, row=0)
    assert isinstance(row, list)


def test_get_row_values_header_row(tmp_path):
    dest = _make_doc(tmp_path)
    row = get_row_values(str(dest), sheet_index=0, row=0)
    assert "Name" in row
    assert "Score" in row


def test_sheet_name_order_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    doc_dict = parse_ods(str(dest))
    names = sheet_name_order(doc_dict)
    assert isinstance(names, list)


def test_sheet_name_order_has_names(tmp_path):
    dest = _make_doc(tmp_path)
    doc_dict = parse_ods(str(dest))
    names = sheet_name_order(doc_dict)
    assert "Alpha" in names
    assert "Beta" in names


def test_get_row_values_data_row(tmp_path):
    dest = _make_doc(tmp_path)
    row = get_row_values(str(dest), sheet_index=0, row=1)
    assert "Alice" in row
