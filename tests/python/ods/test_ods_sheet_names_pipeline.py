"""
test_ods_sheet_names_pipeline.py -- ODS sheet names pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-68
Tests get_sheet_names list, get_sheet_names has correct name, get_row_count sheet0,
get_row_count sheet1, get_cell_value.
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
    get_sheet_names,
    get_row_count,
    get_cell_value,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Prices")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Item"), OdsCell(value="Cost")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Widget"), OdsCell(value="9.99")]))
    sheet2 = OdsSheet(name="Inventory")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Part"), OdsCell(value="Qty")]))
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Bolt"), OdsCell(value="100")]))
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Nut"), OdsCell(value="200")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "multi.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_sheet_names_list(tmp_path):
    dest = _make_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert isinstance(names, list)
    assert len(names) == 2


def test_get_sheet_names_has_prices(tmp_path):
    dest = _make_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Prices" in names


def test_get_row_count_sheet0(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_row_count(str(dest), sheet_index=0)
    assert count == 2


def test_get_row_count_sheet1(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_row_count(str(dest), sheet_index=1)
    assert count == 3


def test_get_cell_value(tmp_path):
    dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val == "Item"
