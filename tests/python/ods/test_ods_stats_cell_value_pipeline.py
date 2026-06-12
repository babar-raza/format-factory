"""
test_ods_stats_cell_value_pipeline.py -- ODS spreadsheet_stats + get_cell_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-92
Tests spreadsheet_stats returns dict, spreadsheet_stats has expected keys,
get_cell_value returns value, get_cell_value correct content, get_cell_value row1.
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
    spreadsheet_stats,
    get_cell_value,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="90")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="75")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return doc, dest


def test_spreadsheet_stats_returns_dict(tmp_path):
    doc, dest = _make_doc(tmp_path)
    doc_dict = parse_ods(str(dest))
    stats = spreadsheet_stats(doc_dict)
    assert isinstance(stats, dict)


def test_spreadsheet_stats_has_keys(tmp_path):
    doc, dest = _make_doc(tmp_path)
    doc_dict = parse_ods(str(dest))
    stats = spreadsheet_stats(doc_dict)
    assert len(stats) > 0


def test_get_cell_value_returns_value(tmp_path):
    doc, dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val is not None


def test_get_cell_value_correct_content(tmp_path):
    doc, dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), sheet_index=0, row=0, col=0)
    assert val == "Name"


def test_get_cell_value_row1(tmp_path):
    doc, dest = _make_doc(tmp_path)
    val = get_cell_value(str(dest), sheet_index=0, row=1, col=0)
    assert val == "Alice"
