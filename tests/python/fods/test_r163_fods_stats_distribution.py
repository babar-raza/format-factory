"""
test_r163_fods_stats_distribution.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT25-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_stats(workbook) -> dict
- workbook_type_distribution(workbook) -> dict
- workbook_sheet_summary(workbook) -> list[dict]
- workbook_empty_rows(workbook) -> dict

Authority: P6 (SAL-FODS-00001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_stats,
    workbook_type_distribution,
    workbook_sheet_summary,
    workbook_empty_rows,
)


def _cell(value=None, value_type="string", formula=None):
    c = {"value": value, "value_type": value_type}
    if formula is not None:
        c["formula"] = formula
    return c


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows, index=0):
    return {"name": name, "rows": rows, "index": index}


def _workbook(sheets):
    return {"sheets": sheets}


# ── workbook_stats ──────────────────────────────────────────────────────

class TestWorkbookStats:

    def test_empty_workbook(self):
        result = workbook_stats(_workbook([]))
        assert result["sheet_count"] == 0
        assert result["total_rows"] == 0
        assert result["total_cells"] == 0
        assert result["non_empty_cells"] == 0
        assert result["formula_cells"] == 0
        assert result["per_sheet"] == []

    def test_single_sheet_basic(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell("b")]),
            _row([_cell(None), _cell("c")]),
        ])])
        result = workbook_stats(wb)
        assert result["sheet_count"] == 1
        assert result["total_rows"] == 2
        assert result["total_cells"] == 4
        assert result["non_empty_cells"] == 3
        assert result["formula_cells"] == 0

    def test_formula_cells_counted(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=SUM(A1:A5)"), _cell("20")]),
        ])])
        result = workbook_stats(wb)
        assert result["formula_cells"] == 1
        assert result["non_empty_cells"] == 2

    def test_multi_sheet(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("x")])], index=0),
            _sheet("B", [_row([_cell("y"), _cell(None)])], index=1),
        ])
        result = workbook_stats(wb)
        assert result["sheet_count"] == 2
        assert result["total_rows"] == 2
        assert result["total_cells"] == 3
        assert result["non_empty_cells"] == 2
        assert len(result["per_sheet"]) == 2
        assert result["per_sheet"][0]["name"] == "A"
        assert result["per_sheet"][1]["name"] == "B"

    def test_per_sheet_breakdown(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell(None), _cell("b", formula="=A1")]),
        ])])
        ps = workbook_stats(wb)["per_sheet"][0]
        assert ps["row_count"] == 1
        assert ps["total_cells"] == 3
        assert ps["non_empty_cells"] == 2
        assert ps["formula_cells"] == 1


# ── workbook_type_distribution ──────────────────────────────────────────

class TestWorkbookTypeDistribution:

    def test_empty_workbook(self):
        result = workbook_type_distribution(_workbook([]))
        assert result["total_cells"] == 0
        assert result["by_type"] == {}
        assert result["per_sheet"] == []

    def test_single_type(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a", "string"), _cell("b", "string")]),
        ])])
        result = workbook_type_distribution(wb)
        assert result["total_cells"] == 2
        assert result["by_type"]["string"] == 2

    def test_mixed_types(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("hello", "string"), _cell("42", "float"),
                  {"value": None}]),
        ])])
        result = workbook_type_distribution(wb)
        assert result["total_cells"] == 3
        assert result["by_type"]["string"] == 1
        assert result["by_type"]["float"] == 1
        assert "empty" in result["by_type"]

    def test_per_sheet_breakdown(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("x", "string")])], index=0),
            _sheet("B", [_row([_cell("1", "float")])], index=1),
        ])
        result = workbook_type_distribution(wb)
        assert len(result["per_sheet"]) == 2
        assert result["per_sheet"][0]["by_type"]["string"] == 1
        assert result["per_sheet"][1]["by_type"]["float"] == 1

    def test_empty_cells_typed_as_empty(self):
        wb = _workbook([_sheet("S1", [_row([{"value": None}])])])
        result = workbook_type_distribution(wb)
        assert result["by_type"].get("empty", 0) >= 1


# ── workbook_sheet_summary ──────────────────────────────────────────────

class TestWorkbookSheetSummary:

    def test_empty_workbook(self):
        assert workbook_sheet_summary(_workbook([])) == []

    def test_single_sheet(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell("b")]),
            _row([_cell(None)]),
        ])])
        result = workbook_sheet_summary(wb)
        assert len(result) == 1
        s = result[0]
        assert s["name"] == "S1"
        assert s["row_count"] == 2
        assert s["cell_count"] == 3
        assert s["non_empty_count"] == 2
        assert s["formula_count"] == 0

    def test_formula_in_summary(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=SUM(A1)")]),
        ])])
        result = workbook_sheet_summary(wb)
        assert result[0]["formula_count"] == 1

    def test_multi_sheet_order(self):
        wb = _workbook([
            _sheet("First", [], index=0),
            _sheet("Second", [_row([_cell("x")])], index=1),
        ])
        result = workbook_sheet_summary(wb)
        assert len(result) == 2
        assert result[0]["name"] == "First"
        assert result[0]["row_count"] == 0
        assert result[1]["name"] == "Second"
        assert result[1]["row_count"] == 1


# ── workbook_empty_rows ─────────────────────────────────────────────────

class TestWorkbookEmptyRows:

    def test_empty_workbook(self):
        result = workbook_empty_rows(_workbook([]))
        assert result["total_empty_rows"] == 0
        assert result["per_sheet"] == []

    def test_no_empty_rows(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 0
        assert result["per_sheet"][0]["empty_row_count"] == 0

    def test_all_empty_rows(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell(None)]),
            _row([_cell(None), _cell(None)]),
        ])])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 2

    def test_mixed_empty_and_filled(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a")]),
            _row([_cell(None)]),
            _row([_cell("b"), _cell(None)]),
        ])])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 1

    def test_row_with_no_cells_is_empty(self):
        wb = _workbook([_sheet("S1", [_row([])])])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 1

    def test_multi_sheet_totals(self):
        wb = _workbook([
            _sheet("A", [_row([_cell(None)])], index=0),
            _sheet("B", [_row([_cell("x")]), _row([_cell(None)])], index=1),
        ])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 2
        assert result["per_sheet"][0]["empty_row_count"] == 1
        assert result["per_sheet"][1]["empty_row_count"] == 1
