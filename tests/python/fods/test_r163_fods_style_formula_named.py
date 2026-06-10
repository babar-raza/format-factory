"""
test_r163_fods_style_formula_named.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT27-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_row_style_summary(workbook) -> dict[str, list[str]]
- workbook_formula_edit_policy(workbook) -> dict
- workbook_named_range_list(workbook) -> list[dict]

Authority: P6 (FACT-FODS-001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_row_style_summary,
    workbook_formula_edit_policy,
    workbook_named_range_list,
)


def _cell(value=None, value_type="string", formula=None, protected=False):
    c = {"value": value, "value_type": value_type}
    if formula is not None:
        c["formula"] = formula
    if protected:
        c["protected"] = True
    return c


def _row(cells, style=None):
    r = {"cells": cells}
    if style:
        r["style"] = style
    return r


def _sheet(name, rows, index=0, named_ranges=None):
    s = {"name": name, "rows": rows, "index": index}
    if named_ranges:
        s["named_ranges"] = named_ranges
    return s


def _workbook(sheets, named_ranges=None):
    wb = {"sheets": sheets}
    if named_ranges:
        wb["named_ranges"] = named_ranges
    return wb


# ── workbook_row_style_summary ──────────────────────────────────────────

class TestWorkbookRowStyleSummary:

    def test_empty_workbook(self):
        assert workbook_row_style_summary(_workbook([])) == {}

    def test_no_styles(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_row_style_summary(wb)
        assert result["S1"] == []

    def test_styled_rows(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a")], style="bold"),
            _row([_cell("b")]),
            _row([_cell("c")], style="italic"),
        ])])
        result = workbook_row_style_summary(wb)
        assert result["S1"] == ["bold", "italic"]

    def test_multi_sheet(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("x")], style="s1")]),
            _sheet("B", [_row([_cell("y")])]),
        ])
        result = workbook_row_style_summary(wb)
        assert result["A"] == ["s1"]
        assert result["B"] == []


# ── workbook_formula_edit_policy ────────────────────────────────────────

class TestWorkbookFormulaEditPolicy:

    def test_no_formulas(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 0
        assert result["policy"] == "no_formulas"

    def test_all_editable(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=SUM(A1)")]),
            _row([_cell("20", formula="=A1+1")]),
        ])])
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 2
        assert result["editable_formulas"] == 2
        assert result["locked_formulas"] == 0
        assert result["policy"] == "all_editable"

    def test_protected_formula(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=SUM(A1)", protected=True)]),
        ])])
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 1
        assert result["locked_formulas"] == 1
        assert result["policy"] == "all_locked"

    def test_mixed_policy(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=A1")]),
            _row([_cell("20", formula="=A2", protected=True)]),
        ])])
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 2
        assert result["editable_formulas"] == 1
        assert result["locked_formulas"] == 1
        assert result["policy"] == "mixed"

    def test_empty_workbook(self):
        result = workbook_formula_edit_policy(_workbook([]))
        assert result["policy"] == "no_formulas"


# ── workbook_named_range_list ───────────────────────────────────────────

class TestWorkbookNamedRangeList:

    def test_empty_workbook(self):
        assert workbook_named_range_list(_workbook([])) == []

    def test_no_named_ranges(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        assert workbook_named_range_list(wb) == []

    def test_workbook_level_ranges(self):
        wb = _workbook([], named_ranges=[
            {"name": "SalesData", "cell_range": "Sheet1.A1:C10"},
        ])
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "SalesData"
        assert result[0]["cell_range"] == "Sheet1.A1:C10"

    def test_sheet_level_ranges(self):
        wb = _workbook([_sheet("S1", [], named_ranges=[
            {"name": "Budget", "cell_range": "S1.D1:D50"},
        ])])
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "Budget"

    def test_string_named_range(self):
        wb = _workbook([], named_ranges=["MyRange"])
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "MyRange"

    def test_multiple_ranges(self):
        wb = _workbook([], named_ranges=[
            {"name": "R1", "cell_range": "A1:A10"},
            {"name": "R2", "cell_range": "B1:B10"},
        ])
        result = workbook_named_range_list(wb)
        assert len(result) == 2
