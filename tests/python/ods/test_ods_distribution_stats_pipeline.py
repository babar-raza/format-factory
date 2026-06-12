"""
test_ods_distribution_stats_pipeline.py -- ODS cell type distribution + stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-50
Tests ods_cell_type_distribution returns dict, ods_data_validation_count,
spreadsheet_stats total_cells, sheet_name_order length, count_sheets.
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
    ods_cell_type_distribution,
    ods_data_validation_count,
    spreadsheet_stats,
    sheet_name_order,
    count_sheets,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Data")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="90")]))
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="80")]))
    sheet2 = OdsSheet(name="Summary")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Total"), OdsCell(value="170")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "stats.ods"
    write_ods(doc, str(dest))
    return dest


def test_ods_cell_type_distribution_is_dict(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    dist = ods_cell_type_distribution(ods_doc)
    assert isinstance(dist, dict)


def test_ods_data_validation_count_zero(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    count = ods_data_validation_count(ods_doc)
    assert count == 0


def test_spreadsheet_stats_total_cells(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    stats = spreadsheet_stats(ods_doc)
    assert stats["total_cells"] >= 7  # 3 rows x 2 cols + 1 row x 2 cols


def test_sheet_name_order_length(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    order = sheet_name_order(ods_doc)
    assert len(order) == 2


def test_count_sheets_two(tmp_path):
    dest = _make_doc(tmp_path)
    assert count_sheets(str(dest)) == 2
