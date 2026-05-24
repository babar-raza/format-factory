"""
test_r61_fods_deepening.py — R61 Train G: FODS product deepening.

Tests 2 new R61 FODS capabilities:
  - workbook_formula_list: flat list of all formula cells
  - workbook_cell_range: 2D value slice from a sheet

R61 Sprint: FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fods.neutral_model import workbook_formula_list, workbook_cell_range


def _make_workbook(sheets=None):
    return {"format_id": "fods", "sheets": sheets or []}


def _make_sheet(name, rows, index=0):
    return {"name": name, "index": index, "rows": rows}


def _make_row(cells):
    return {"cells": cells}


def _make_cell(value=None, formula=None):
    c = {"value": value}
    if formula is not None:
        c["formula"] = formula
    return c


class TestWorkbookFormulaList:
    """workbook_formula_list returns flat list of formula cells."""

    def test_empty_workbook_returns_empty_list(self):
        wb = _make_workbook()
        result = workbook_formula_list(wb)
        assert result == []

    def test_no_formulas_returns_empty_list(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(42), _make_cell("hello")]),
        ])])
        result = workbook_formula_list(wb)
        assert result == []

    def test_single_formula_cell(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(10), _make_cell(value=55, formula="=SUM(A1:A5)")]),
        ])])
        result = workbook_formula_list(wb)
        assert len(result) == 1
        assert result[0]["formula"] == "=SUM(A1:A5)"
        assert result[0]["value"] == 55
        assert result[0]["sheet_name"] == "Sheet1"
        assert result[0]["row_index"] == 0
        assert result[0]["col_index"] == 1

    def test_multiple_formula_cells_across_sheets(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [
                _make_row([_make_cell(value=10, formula="=A1+B1"), _make_cell(5)]),
            ], index=0),
            _make_sheet("Sheet2", [
                _make_row([_make_cell(100)]),
                _make_row([_make_cell(value=200, formula="=SUM(A:A)")]),
            ], index=1),
        ])
        result = workbook_formula_list(wb)
        assert len(result) == 2
        formulas = [r["formula"] for r in result]
        assert "=A1+B1" in formulas
        assert "=SUM(A:A)" in formulas

    def test_formula_result_has_all_fields(self):
        wb = _make_workbook([_make_sheet("Data", [
            _make_row([_make_cell(value=99, formula="=MAX(A1:A10)")]),
        ])])
        result = workbook_formula_list(wb)
        assert len(result) == 1
        entry = result[0]
        assert "sheet_name" in entry
        assert "sheet_index" in entry
        assert "row_index" in entry
        assert "col_index" in entry
        assert "formula" in entry
        assert "value" in entry

    def test_formula_without_cached_value(self):
        wb = _make_workbook([_make_sheet("Calc", [
            _make_row([_make_cell(formula="=A1*2")]),
        ])])
        result = workbook_formula_list(wb)
        assert len(result) == 1
        assert result[0]["value"] is None
        assert result[0]["formula"] == "=A1*2"


class TestWorkbookCellRange:
    """workbook_cell_range returns a 2D list of cell values."""

    def test_empty_workbook_returns_empty(self):
        wb = _make_workbook()
        result = workbook_cell_range(wb)
        assert result == []

    def test_invalid_sheet_index_returns_empty(self):
        wb = _make_workbook([_make_sheet("Sheet1", [])])
        result = workbook_cell_range(wb, sheet_index=99)
        assert result == []

    def test_full_sheet_range(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(1), _make_cell(2), _make_cell(3)]),
            _make_row([_make_cell(4), _make_cell(5), _make_cell(6)]),
        ])])
        result = workbook_cell_range(wb)
        assert result == [[1, 2, 3], [4, 5, 6]]

    def test_row_slice(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(1), _make_cell(2)]),
            _make_row([_make_cell(3), _make_cell(4)]),
            _make_row([_make_cell(5), _make_cell(6)]),
        ])])
        result = workbook_cell_range(wb, row_start=1, row_end=2)
        assert result == [[3, 4], [5, 6]]

    def test_col_slice(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(1), _make_cell(2), _make_cell(3)]),
        ])])
        result = workbook_cell_range(wb, col_start=1, col_end=2)
        assert result == [[2, 3]]

    def test_subrange(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(1), _make_cell(2), _make_cell(3)]),
            _make_row([_make_cell(4), _make_cell(5), _make_cell(6)]),
            _make_row([_make_cell(7), _make_cell(8), _make_cell(9)]),
        ])])
        result = workbook_cell_range(wb, row_start=0, row_end=1, col_start=1, col_end=2)
        assert result == [[2, 3], [5, 6]]

    def test_none_values_preserved(self):
        wb = _make_workbook([_make_sheet("Sheet1", [
            _make_row([_make_cell(None), _make_cell(42)]),
        ])])
        result = workbook_cell_range(wb)
        assert result == [[None, 42]]

    def test_second_sheet(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell(1)])], index=0),
            _make_sheet("Sheet2", [_make_row([_make_cell(99)])], index=1),
        ])
        result = workbook_cell_range(wb, sheet_index=1)
        assert result == [[99]]
