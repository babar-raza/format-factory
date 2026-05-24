"""
test_r62_ods_stats.py — R62 Train I: ODS stats API tests.

Tests the two new capability functions added to src/python/ods/ods_stats.py:
  - spreadsheet_stats(): aggregate sheet/row/cell statistics
  - sheet_name_order(): ordered list of sheet names

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from ods.ods_stats import spreadsheet_stats, sheet_name_order


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cell(value="", value_type="string", text=""):
    return {"value": value, "value_type": value_type, "text": text}


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows):
    return {"name": name, "row_count": len(rows), "rows": rows}


def _doc(sheets):
    return {"ok": True, "sheet_count": len(sheets), "sheets": sheets}


# ---------------------------------------------------------------------------
# spreadsheet_stats
# ---------------------------------------------------------------------------

class TestSpreadsheetStatsEmpty:
    def test_empty_doc_returns_zeros(self):
        result = spreadsheet_stats(_doc([]))
        assert result["sheet_count"] == 0
        assert result["total_rows"] == 0
        assert result["total_cells"] == 0
        assert result["non_empty_cells"] == 0
        assert result["per_sheet"] == []

    def test_returns_dict(self):
        assert isinstance(spreadsheet_stats(_doc([])), dict)

    def test_single_empty_sheet(self):
        result = spreadsheet_stats(_doc([_sheet("S1", [])]))
        assert result["sheet_count"] == 1
        assert result["total_rows"] == 0

    def test_sheet_with_no_cells(self):
        result = spreadsheet_stats(_doc([_sheet("S1", [_row([])])]))
        assert result["total_rows"] == 1
        assert result["total_cells"] == 0


class TestSpreadsheetStatsContent:
    def test_single_cell(self):
        sheet = _sheet("S1", [_row([_cell("hello")])])
        result = spreadsheet_stats(_doc([sheet]))
        assert result["total_cells"] == 1
        assert result["sheet_count"] == 1

    def test_multiple_cells_per_row(self):
        cells = [_cell("a"), _cell("b"), _cell("c")]
        sheet = _sheet("S1", [_row(cells)])
        result = spreadsheet_stats(_doc([sheet]))
        assert result["total_cells"] == 3

    def test_multiple_rows(self):
        rows = [_row([_cell("x"), _cell("y")]) for _ in range(4)]
        sheet = _sheet("S1", rows)
        result = spreadsheet_stats(_doc([sheet]))
        assert result["total_rows"] == 4
        assert result["total_cells"] == 8

    def test_multi_sheet_totals(self):
        s1 = _sheet("S1", [_row([_cell("a"), _cell("b")])])
        s2 = _sheet("S2", [_row([_cell("c")])])
        result = spreadsheet_stats(_doc([s1, s2]))
        assert result["sheet_count"] == 2
        assert result["total_cells"] == 3

    def test_per_sheet_breakdown(self):
        s1 = _sheet("Alpha", [_row([_cell("x")])])
        s2 = _sheet("Beta", [_row([_cell("y"), _cell("z")])])
        result = spreadsheet_stats(_doc([s1, s2]))
        per = result["per_sheet"]
        assert len(per) == 2
        assert per[0]["name"] == "Alpha"
        assert per[0]["cell_count"] == 1
        assert per[1]["name"] == "Beta"
        assert per[1]["cell_count"] == 2

    def test_per_sheet_has_required_keys(self):
        s = _sheet("S1", [_row([_cell("x")])])
        result = spreadsheet_stats(_doc([s]))
        entry = result["per_sheet"][0]
        for key in ("name", "row_count", "cell_count", "non_empty_cells"):
            assert key in entry, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# sheet_name_order
# ---------------------------------------------------------------------------

class TestSheetNameOrder:
    def test_empty_doc_returns_empty_list(self):
        assert sheet_name_order(_doc([])) == []

    def test_single_sheet(self):
        assert sheet_name_order(_doc([_sheet("MySheet", [])])) == ["MySheet"]

    def test_multiple_sheets_order_preserved(self):
        sheets = [_sheet("First", []), _sheet("Second", []), _sheet("Third", [])]
        result = sheet_name_order(_doc(sheets))
        assert result == ["First", "Second", "Third"]

    def test_order_not_alphabetically_sorted(self):
        sheets = [_sheet("Zebra", []), _sheet("Apple", []), _sheet("Mango", [])]
        result = sheet_name_order(_doc(sheets))
        assert result == ["Zebra", "Apple", "Mango"]

    def test_returns_list_of_strings(self):
        sheets = [_sheet("A", []), _sheet("B", [])]
        result = sheet_name_order(_doc(sheets))
        assert all(isinstance(n, str) for n in result)
