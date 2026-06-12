"""
test_ods_write_sheet_pipeline.py -- ODS write + sheet query pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-40
Tests write_ods produces valid file, get_sheet_names after write,
get_row_count for each sheet, ods_to_csv has data, get_all_values flat.
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
    get_row_count,
    ods_to_csv,
    get_all_values,
    count_sheets,
)
from ods.ods_writer import write_ods


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Alpha")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="X"), OdsCell(value="Y")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    sheet2 = OdsSheet(name="Beta")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="A")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "multi.ods"
    write_ods(doc, str(dest))
    return dest


def test_get_sheet_names_two_sheets(tmp_path):
    dest = _make_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Alpha" in names
    assert "Beta" in names


def test_get_row_count_sheet1(tmp_path):
    dest = _make_doc(tmp_path)
    assert get_row_count(str(dest), sheet_index=0) == 2


def test_get_row_count_sheet2(tmp_path):
    dest = _make_doc(tmp_path)
    assert get_row_count(str(dest), sheet_index=1) == 1


def test_ods_to_csv_contains_data(tmp_path):
    dest = _make_doc(tmp_path)
    csv_str = ods_to_csv(str(dest), sheet_index=0)
    assert "X" in csv_str


def test_count_sheets_two(tmp_path):
    dest = _make_doc(tmp_path)
    assert count_sheets(str(dest)) == 2
