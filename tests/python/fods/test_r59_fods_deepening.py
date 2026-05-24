"""
test_r59_fods_deepening.py — R59 Train G: FODS product deepening.

New capabilities tested:
1. workbook_type_distribution() — cell value_type distribution
2. find_sheet_by_name() — find sheet by name, returns dict or None

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fods.neutral_model import (
    workbook_type_distribution,
    find_sheet_by_name,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_workbook(sheets):
    """Build a minimal workbook dict for testing."""
    return {
        "format_id": "fods",
        "spec_version": "1.3",
        "odf_version_attr": "1.3",
        "mimetype": None,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


def _make_sheet(name, index, rows):
    return {"name": name, "index": index, "row_count": len(rows), "rows": rows}


def _make_row(index, cells):
    return {"index": index, "cells": cells}


def _make_cell(value=None, value_type=None, formula=None):
    c = {"value": value}
    if value_type is not None:
        c["value_type"] = value_type
    if formula is not None:
        c["formula"] = formula
    return c


# ---------------------------------------------------------------------------
# workbook_type_distribution tests
# ---------------------------------------------------------------------------

class TestWorkbookTypeDistribution:

    def test_empty_workbook_returns_empty_distribution(self):
        wb = _make_workbook([])
        result = workbook_type_distribution(wb)
        assert result["by_type"] == {}
        assert result["total_cells"] == 0
        assert result["per_sheet"] == []

    def test_single_float_cell(self):
        row = _make_row(0, [_make_cell(1.5, "float")])
        sheet = _make_sheet("Sheet1", 0, [row])
        wb = _make_workbook([sheet])
        result = workbook_type_distribution(wb)
        assert result["by_type"]["float"] == 1
        assert result["total_cells"] == 1

    def test_mixed_types(self):
        cells = [
            _make_cell(1, "float"),
            _make_cell("hello", "string"),
            _make_cell(None, None),       # empty (no value_type, value is None)
            _make_cell(True, "boolean"),
            _make_cell(0.5, "percentage"),
        ]
        row = _make_row(0, cells)
        sheet = _make_sheet("Sheet1", 0, [row])
        wb = _make_workbook([sheet])
        result = workbook_type_distribution(wb)
        assert result["by_type"]["float"] == 1
        assert result["by_type"]["string"] == 1
        assert result["by_type"]["boolean"] == 1
        assert result["by_type"]["percentage"] == 1
        assert result["total_cells"] == 5

    def test_null_value_without_type_is_empty(self):
        """Cell with value=None and no value_type must count as 'empty'."""
        row = _make_row(0, [_make_cell(None)])
        sheet = _make_sheet("Sheet1", 0, [row])
        wb = _make_workbook([sheet])
        result = workbook_type_distribution(wb)
        assert result["by_type"].get("empty", 0) >= 1

    def test_per_sheet_breakdown_matches_totals(self):
        cells_a = [_make_cell(1, "float"), _make_cell(2, "float")]
        cells_b = [_make_cell("x", "string")]
        sheet_a = _make_sheet("A", 0, [_make_row(0, cells_a)])
        sheet_b = _make_sheet("B", 1, [_make_row(0, cells_b)])
        wb = _make_workbook([sheet_a, sheet_b])
        result = workbook_type_distribution(wb)
        assert result["total_cells"] == 3
        assert result["by_type"]["float"] == 2
        assert result["by_type"]["string"] == 1
        per = {s["name"]: s["by_type"] for s in result["per_sheet"]}
        assert per["A"]["float"] == 2
        assert per["B"]["string"] == 1

    def test_formula_cells_counted_by_value_type(self):
        """Formula cells are typed by value_type, not by 'formula'."""
        cell = _make_cell(10, "float", formula="of:=SUM(A1:A5)")
        row = _make_row(0, [cell])
        sheet = _make_sheet("Sheet1", 0, [row])
        wb = _make_workbook([sheet])
        result = workbook_type_distribution(wb)
        assert result["by_type"]["float"] == 1

    def test_multiple_sheets_aggregate_correctly(self):
        sheets = [
            _make_sheet(f"S{i}", i, [_make_row(0, [_make_cell(i, "float")])])
            for i in range(5)
        ]
        wb = _make_workbook(sheets)
        result = workbook_type_distribution(wb)
        assert result["total_cells"] == 5
        assert result["by_type"]["float"] == 5
        assert len(result["per_sheet"]) == 5


# ---------------------------------------------------------------------------
# find_sheet_by_name tests
# ---------------------------------------------------------------------------

class TestFindSheetByName:

    def test_find_existing_sheet(self):
        sheet = _make_sheet("Budget", 0, [])
        wb = _make_workbook([sheet])
        result = find_sheet_by_name(wb, "Budget")
        assert result is not None
        assert result["name"] == "Budget"
        assert result["index"] == 0

    def test_returns_none_for_missing_name(self):
        sheet = _make_sheet("Budget", 0, [])
        wb = _make_workbook([sheet])
        result = find_sheet_by_name(wb, "Sales")
        assert result is None

    def test_case_sensitive_match(self):
        """Name match is case-sensitive."""
        sheet = _make_sheet("Budget", 0, [])
        wb = _make_workbook([sheet])
        assert find_sheet_by_name(wb, "budget") is None
        assert find_sheet_by_name(wb, "BUDGET") is None
        assert find_sheet_by_name(wb, "Budget") is not None

    def test_returns_first_match_when_duplicate_names(self):
        """If two sheets have the same name, first is returned."""
        s0 = _make_sheet("dup", 0, [])
        s1 = _make_sheet("dup", 1, [])
        wb = _make_workbook([s0, s1])
        result = find_sheet_by_name(wb, "dup")
        assert result["index"] == 0

    def test_empty_workbook_returns_none(self):
        wb = _make_workbook([])
        assert find_sheet_by_name(wb, "Anything") is None

    def test_returned_sheet_includes_rows(self):
        """Returned dict is the full sheet including rows."""
        row = _make_row(0, [_make_cell(42, "float")])
        sheet = _make_sheet("Data", 0, [row])
        wb = _make_workbook([sheet])
        result = find_sheet_by_name(wb, "Data")
        assert len(result["rows"]) == 1
        assert result["rows"][0]["cells"][0]["value"] == 42
