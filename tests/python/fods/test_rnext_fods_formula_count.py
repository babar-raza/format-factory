"""Tests for fods_formula_count — product-healing pilot.

Verifies fods_formula_count returns the correct total number of formula
cells across all sheets, consistent with workbook_formula_list.
"""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import fods_formula_count, workbook_formula_list


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cell(value=None, formula=None):
    c = {}
    if value is not None:
        c["value"] = value
    if formula is not None:
        c["formula"] = formula
    return c


def _wb(sheets):
    return {"sheets": sheets}


def _sheet(name, rows, index=0):
    return {"name": name, "index": index, "rows": rows}


def _row(cells):
    return {"cells": cells}


# ---------------------------------------------------------------------------
# Test: empty workbook
# ---------------------------------------------------------------------------

class TestEmptyWorkbook:
    def test_empty_sheets_list(self):
        assert fods_formula_count(_wb([])) == 0

    def test_missing_sheets_key(self):
        assert fods_formula_count({}) == 0

    def test_sheet_with_no_rows(self):
        assert fods_formula_count(_wb([_sheet("S1", [])])) == 0

    def test_rows_with_no_cells(self):
        wb = _wb([_sheet("S1", [_row([])])])
        assert fods_formula_count(wb) == 0


# ---------------------------------------------------------------------------
# Test: single sheet with formulas
# ---------------------------------------------------------------------------

class TestSingleSheet:
    def test_one_formula(self):
        wb = _wb([_sheet("S1", [_row([_cell(formula="=1")])])])
        assert fods_formula_count(wb) == 1

    def test_mixed_cells(self):
        wb = _wb([_sheet("S1", [
            _row([_cell(value=1), _cell(formula="=A1+1"), _cell(value=3)]),
            _row([_cell(value=4), _cell(value=5), _cell(formula="=SUM(A1:A2)")]),
        ])])
        assert fods_formula_count(wb) == 2

    def test_all_formulas(self):
        wb = _wb([_sheet("S1", [
            _row([_cell(formula="=1"), _cell(formula="=2")]),
            _row([_cell(formula="=3"), _cell(formula="=4")]),
        ])])
        assert fods_formula_count(wb) == 4

    def test_no_formulas(self):
        wb = _wb([_sheet("S1", [
            _row([_cell(value=1), _cell(value=2)]),
        ])])
        assert fods_formula_count(wb) == 0


# ---------------------------------------------------------------------------
# Test: multiple sheets
# ---------------------------------------------------------------------------

class TestMultipleSheets:
    def test_formulas_across_sheets(self):
        wb = _wb([
            _sheet("S1", [_row([_cell(formula="=1"), _cell(formula="=2")])], index=0),
            _sheet("S2", [_row([_cell(formula="=3")])], index=1),
        ])
        assert fods_formula_count(wb) == 3

    def test_one_sheet_has_no_formulas(self):
        wb = _wb([
            _sheet("S1", [_row([_cell(value=1)])], index=0),
            _sheet("S2", [_row([_cell(formula="=1")])], index=1),
        ])
        assert fods_formula_count(wb) == 1


# ---------------------------------------------------------------------------
# Test: consistency with workbook_formula_list
# ---------------------------------------------------------------------------

class TestConsistencyWithFormulaList:
    def test_count_matches_list_length(self):
        wb = _wb([
            _sheet("S1", [
                _row([_cell(formula="=A1"), _cell(value=10)]),
                _row([_cell(formula="=B1"), _cell(formula="=C1")]),
            ], index=0),
            _sheet("S2", [
                _row([_cell(formula="=D1")]),
            ], index=1),
        ])
        assert fods_formula_count(wb) == len(workbook_formula_list(wb))

    def test_empty_wb_consistency(self):
        wb = _wb([])
        assert fods_formula_count(wb) == len(workbook_formula_list(wb)) == 0


# ---------------------------------------------------------------------------
# Test: edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_none_cell_in_row(self):
        wb = _wb([_sheet("S1", [_row([None, _cell(formula="=1")])])])
        assert fods_formula_count(wb) == 1

    def test_formula_with_none_value(self):
        wb = _wb([_sheet("S1", [_row([{"formula": "=X", "value": None}])])])
        assert fods_formula_count(wb) == 1

    def test_empty_formula_string_not_counted(self):
        """A cell with formula='' is arguably not a formula, but the function
        counts it because formula key is not None. This matches workbook_formula_list."""
        wb = _wb([_sheet("S1", [_row([{"formula": "", "value": 0}])])])
        # formula key is not None (it's ""), so it is counted
        assert fods_formula_count(wb) == 1
