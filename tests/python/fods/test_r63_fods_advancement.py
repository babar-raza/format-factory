"""
test_r63_fods_advancement.py — R63 Train H: FODS product advancement.

New capabilities added in R63:
1. workbook_numeric_summary(workbook)   — per-sheet numeric min/max/sum/count
2. workbook_column_count(workbook)      — used column width per sheet

These functions extend the R62 capabilities (workbook_merged_cell_summary,
workbook_sheet_order) with numeric analysis and column-width analysis.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train H — FODS product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    build_workbook,
    workbook_numeric_summary,
    workbook_column_count,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_workbook(sheets_data: list) -> dict:
    """Build a minimal workbook for testing."""
    sheets = []
    for sheet_name, rows_data in sheets_data:
        rows = []
        for row_cells in rows_data:
            cells = []
            for val, vtype in row_cells:
                cells.append({"value": val, "value_type": vtype})
            rows.append({"cells": cells})
        sheets.append({"name": sheet_name, "rows": rows})
    return {
        "sheets": sheets,
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


# ---------------------------------------------------------------------------
# workbook_numeric_summary tests
# ---------------------------------------------------------------------------

class TestWorkbookNumericSummary:
    """Tests for workbook_numeric_summary()."""

    def test_empty_workbook_returns_zero_count(self):
        wb = _make_workbook([])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 0
        assert result["global_min"] is None
        assert result["global_max"] is None
        assert result["per_sheet"] == []

    def test_workbook_with_float_cells(self):
        wb = _make_workbook([
            ("Sheet1", [
                [(1.5, "float"), (2.5, "float")],
                [(3.0, "float"), (None, "empty")],
            ])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 3
        assert result["global_min"] == 1.5
        assert result["global_max"] == 3.0
        assert result["global_sum"] == 7.0

    def test_workbook_with_int_cells(self):
        wb = _make_workbook([
            ("Sheet1", [
                [(10, "int"), (20, "int")],
            ])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 2
        assert result["global_sum"] == 30

    def test_string_cells_excluded(self):
        wb = _make_workbook([
            ("Sheet1", [
                [("hello", "string"), (5.0, "float")],
            ])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 1
        assert result["global_sum"] == 5.0

    def test_per_sheet_breakdown(self):
        wb = _make_workbook([
            ("Sales", [[(100.0, "float"), (200.0, "float")]]),
            ("Expenses", [[(50.0, "float")]]),
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 3
        per_sheet = {s["sheet_name"]: s for s in result["per_sheet"]}
        assert per_sheet["Sales"]["numeric_count"] == 2
        assert per_sheet["Expenses"]["numeric_count"] == 1

    def test_sheet_with_no_numeric_cells(self):
        wb = _make_workbook([
            ("TextOnly", [[("hello", "string"), ("world", "string")]]),
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 0
        assert result["per_sheet"][0]["numeric_count"] == 0
        assert result["per_sheet"][0]["min_value"] is None

    def test_negative_values_tracked(self):
        wb = _make_workbook([
            ("Sheet1", [[(-10.0, "float"), (5.0, "float")]]),
        ])
        result = workbook_numeric_summary(wb)
        assert result["global_min"] == -10.0
        assert result["global_max"] == 5.0
        assert result["global_sum"] == -5.0

    def test_single_cell_workbook(self):
        wb = _make_workbook([("Sheet1", [[(42.0, "float")]])])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 1
        assert result["global_min"] == 42.0
        assert result["global_max"] == 42.0


# ---------------------------------------------------------------------------
# workbook_column_count tests
# ---------------------------------------------------------------------------

class TestWorkbookColumnCount:
    """Tests for workbook_column_count()."""

    def test_empty_workbook(self):
        wb = _make_workbook([])
        result = workbook_column_count(wb)
        assert result["total_sheets"] == 0
        assert result["per_sheet"] == []

    def test_single_sheet_column_count(self):
        wb = _make_workbook([
            ("Sheet1", [
                [(1.0, "float"), (2.0, "float"), (3.0, "float")],
                [(4.0, "float")],
            ])
        ])
        result = workbook_column_count(wb)
        assert result["total_sheets"] == 1
        sheet = result["per_sheet"][0]
        assert sheet["sheet_name"] == "Sheet1"
        assert sheet["max_columns"] == 3  # widest row has 3 non-None cells
        assert sheet["row_count"] == 2

    def test_empty_cells_not_counted(self):
        """None values should not count toward column width."""
        wb = _make_workbook([
            ("Sheet1", [
                [(1.0, "float"), (None, "empty"), (None, "empty")],
                [(2.0, "float"), (3.0, "float")],
            ])
        ])
        result = workbook_column_count(wb)
        sheet = result["per_sheet"][0]
        assert sheet["max_columns"] == 2  # second row is widest (2 non-None)

    def test_multiple_sheets(self):
        wb = _make_workbook([
            ("Sheet1", [[(1.0, "float"), (2.0, "float")]]),
            ("Sheet2", [[(1.0, "float"), (2.0, "float"), (3.0, "float"), (4.0, "float")]]),
        ])
        result = workbook_column_count(wb)
        assert result["total_sheets"] == 2
        by_name = {s["sheet_name"]: s for s in result["per_sheet"]}
        assert by_name["Sheet1"]["max_columns"] == 2
        assert by_name["Sheet2"]["max_columns"] == 4

    def test_empty_sheet_returns_zero_columns(self):
        wb = _make_workbook([("Empty", [])])
        result = workbook_column_count(wb)
        assert result["per_sheet"][0]["max_columns"] == 0
        assert result["per_sheet"][0]["row_count"] == 0

    def test_sheet_with_all_none_cells(self):
        wb = _make_workbook([
            ("AllNone", [[(None, "empty"), (None, "empty")]]),
        ])
        result = workbook_column_count(wb)
        assert result["per_sheet"][0]["max_columns"] == 0

    def test_returns_correct_keys(self):
        wb = _make_workbook([("Sheet1", [[(1.0, "float")]])])
        result = workbook_column_count(wb)
        assert "per_sheet" in result
        assert "total_sheets" in result
        sheet = result["per_sheet"][0]
        assert "sheet_name" in sheet
        assert "max_columns" in sheet
        assert "row_count" in sheet


# ---------------------------------------------------------------------------
# API accessibility tests
# ---------------------------------------------------------------------------

class TestTrainHFodsApiAccess:
    """New R63 functions must be accessible from the fods package."""

    def test_workbook_numeric_summary_callable(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_numeric_summary")
        assert callable(fods.workbook_numeric_summary)

    def test_workbook_column_count_callable(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_column_count")
        assert callable(fods.workbook_column_count)

    def test_all_r63_new_apis_in_all(self):
        import src.python.fods as fods
        for api in ["workbook_numeric_summary", "workbook_column_count"]:
            assert api in fods.__all__, f"{api} must be in fods.__all__"
