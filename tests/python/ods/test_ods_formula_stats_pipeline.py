"""
test_ods_formula_stats_pipeline.py -- ODS formula + stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-56
Tests ods_formula_cell_count int, ods_data_validation_count zero,
spreadsheet_stats has total_cells, count_sheets, ods_sheet_name_list.
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
    parse_ods,
    count_sheets,
    ods_formula_cell_count,
    ods_data_validation_count,
    spreadsheet_stats,
    ods_sheet_name_list,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Alpha")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="1"), OdsCell(value="2")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="3"), OdsCell(value="4")]))
    sheet2 = OdsSheet(name="Beta")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="X"), OdsCell(value="Y")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_ods_formula_cell_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    result = ods_formula_cell_count(ods_doc)
    assert isinstance(result, int)


def test_ods_data_validation_count_zero(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    result = ods_data_validation_count(ods_doc)
    assert result == 0


def test_spreadsheet_stats_total_cells(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    stats = spreadsheet_stats(ods_doc)
    assert "total_cells" in stats
    assert stats["total_cells"] >= 8


def test_count_sheets_two(tmp_path):
    dest = _make_doc(tmp_path)
    assert count_sheets(str(dest)) == 2


def test_ods_sheet_name_list(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    names = ods_sheet_name_list(ods_doc)
    assert "Alpha" in names
    assert "Beta" in names
