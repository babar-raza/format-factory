"""
test_r163_fods_formula_sheet_mgmt.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT25-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_formula_list(workbook) -> list[dict]
- workbook_add_sheet(workbook, name, position) -> (bool, str)
- workbook_rename_sheet(workbook, old, new) -> (bool, str)
- workbook_remove_sheet(workbook, name) -> (bool, str)

Authority: P6 (FACT-FODS-001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_formula_list,
    workbook_add_sheet,
    workbook_rename_sheet,
    workbook_remove_sheet,
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


# ── workbook_formula_list ───────────────────────────────────────────────

class TestWorkbookFormulaList:

    def test_empty_workbook(self):
        assert workbook_formula_list(_workbook([])) == []

    def test_no_formulas(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a"), _cell("b")])])])
        assert workbook_formula_list(wb) == []

    def test_single_formula(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", formula="=SUM(A1:A5)")]),
        ])])
        result = workbook_formula_list(wb)
        assert len(result) == 1
        assert result[0]["formula"] == "=SUM(A1:A5)"
        assert result[0]["value"] == "10"
        assert result[0]["row_index"] == 0
        assert result[0]["col_index"] == 0
        assert result[0]["sheet_name"] == "S1"

    def test_multiple_formulas(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("5", formula="=A1"), _cell("x")]),
            _row([_cell("10", formula="=B1")]),
        ])])
        result = workbook_formula_list(wb)
        assert len(result) == 2
        assert result[0]["row_index"] == 0
        assert result[0]["col_index"] == 0
        assert result[1]["row_index"] == 1
        assert result[1]["col_index"] == 0

    def test_formulas_across_sheets(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("1", formula="=1")])], index=0),
            _sheet("B", [_row([_cell("2", formula="=2")])], index=1),
        ])
        result = workbook_formula_list(wb)
        assert len(result) == 2
        assert result[0]["sheet_name"] == "A"
        assert result[1]["sheet_name"] == "B"

    def test_formula_with_none_value(self):
        wb = _workbook([_sheet("S1", [_row([_cell(None, formula="=NOW()")])])])
        result = workbook_formula_list(wb)
        assert len(result) == 1
        assert result[0]["value"] is None


# ── workbook_add_sheet ──────────────────────────────────────────────────

class TestWorkbookAddSheet:

    def test_add_to_empty(self):
        wb = _workbook([])
        ok, msg = workbook_add_sheet(wb, "New")
        assert ok is True
        assert len(wb["sheets"]) == 1
        assert wb["sheets"][0]["name"] == "New"

    def test_add_appends(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_add_sheet(wb, "S2")
        assert ok is True
        assert wb["sheets"][-1]["name"] == "S2"

    def test_add_at_position(self):
        wb = _workbook([_sheet("A", []), _sheet("C", [])])
        ok, msg = workbook_add_sheet(wb, "B", position=1)
        assert ok is True
        assert wb["sheets"][1]["name"] == "B"

    def test_duplicate_name_rejected(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_add_sheet(wb, "S1")
        assert ok is False

    def test_empty_name_rejected(self):
        wb = _workbook([])
        ok, msg = workbook_add_sheet(wb, "")
        assert ok is False

    def test_whitespace_name_rejected(self):
        wb = _workbook([])
        ok, msg = workbook_add_sheet(wb, "   ")
        assert ok is False


# ── workbook_rename_sheet ───────────────────────────────────────────────

class TestWorkbookRenameSheet:

    def test_rename_success(self):
        wb = _workbook([_sheet("Old", [])])
        ok, msg = workbook_rename_sheet(wb, "Old", "New")
        assert ok is True
        assert wb["sheets"][0]["name"] == "New"

    def test_rename_nonexistent(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_rename_sheet(wb, "S99", "X")
        assert ok is False

    def test_rename_to_existing(self):
        wb = _workbook([_sheet("A", []), _sheet("B", [])])
        ok, msg = workbook_rename_sheet(wb, "A", "B")
        assert ok is False

    def test_rename_to_same_name(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_rename_sheet(wb, "S1", "S1")
        assert ok is True

    def test_rename_empty_name_rejected(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_rename_sheet(wb, "S1", "")
        assert ok is False


# ── workbook_remove_sheet ───────────────────────────────────────────────

class TestWorkbookRemoveSheet:

    def test_remove_one_of_many(self):
        wb = _workbook([_sheet("A", []), _sheet("B", [])])
        ok, msg = workbook_remove_sheet(wb, "A")
        assert ok is True
        assert len(wb["sheets"]) == 1
        assert wb["sheets"][0]["name"] == "B"

    def test_remove_last_sheet_rejected(self):
        wb = _workbook([_sheet("Only", [])])
        ok, msg = workbook_remove_sheet(wb, "Only")
        assert ok is False
        assert len(wb["sheets"]) == 1

    def test_remove_nonexistent(self):
        wb = _workbook([_sheet("S1", [])])
        ok, msg = workbook_remove_sheet(wb, "S99")
        assert ok is False
