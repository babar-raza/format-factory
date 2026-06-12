"""
test_ods_multisheet_stats_pipeline.py -- ODS multisheet stats aggregation pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-44
Tests spreadsheet_stats keys, ods_sheet_name_list, ods_cell_type_distribution,
sheet_name_order, ods_formula_cell_count on a multi-sheet doc.
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
    spreadsheet_stats,
    ods_sheet_name_list,
    ods_cell_type_distribution,
    sheet_name_order,
    ods_formula_cell_count,
    parse_ods,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Revenue")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Q1"), OdsCell(value="1000")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Q2"), OdsCell(value="2000")]))
    sheet2 = OdsSheet(name="Costs")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Q1"), OdsCell(value="500")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "multi.ods"
    write_ods(doc, str(dest))
    return dest, doc


def test_spreadsheet_stats_has_keys(tmp_path):
    dest, doc = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    stats = spreadsheet_stats(ods_doc)
    assert "sheet_count" in stats
    assert "total_cells" in stats


def test_ods_sheet_name_list(tmp_path):
    dest, doc = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    names = ods_sheet_name_list(ods_doc)
    assert "Revenue" in names
    assert "Costs" in names


def test_ods_cell_type_distribution(tmp_path):
    dest, doc = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    dist = ods_cell_type_distribution(ods_doc)
    assert isinstance(dist, dict)


def test_sheet_name_order(tmp_path):
    dest, doc = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    order = sheet_name_order(ods_doc)
    assert order[0] == "Revenue"
    assert order[1] == "Costs"


def test_formula_cell_count_zero(tmp_path):
    dest, doc = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    count = ods_formula_cell_count(ods_doc)
    assert count == 0
