"""
test_r162_fods_sheet_order_numeric.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_sheet_order(workbook) -> list[str]
- workbook_numeric_summary(workbook) -> dict
- workbook_column_count(workbook) -> dict

Authority: P6 (FACT-FODS-001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_sheet_order,
    workbook_numeric_summary,
    workbook_column_count,
)


def _cell(value=None, value_type="string"):
    return {"value": value, "value_type": value_type}


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows):
    return {"name": name, "rows": rows}


def _workbook(sheets):
    return {"sheets": sheets}


# --- workbook_sheet_order tests ---

class TestWorkbookSheetOrder:

    def test_single_sheet(self):
        wb = _workbook([_sheet("Sheet1", [])])
        assert workbook_sheet_order(wb) == ["Sheet1"]

    def test_multiple_sheets_preserves_order(self):
        wb = _workbook([
            _sheet("Alpha", []),
            _sheet("Beta", []),
            _sheet("Gamma", []),
        ])
        assert workbook_sheet_order(wb) == ["Alpha", "Beta", "Gamma"]

    def test_empty_workbook(self):
        wb = _workbook([])
        assert workbook_sheet_order(wb) == []

    def test_missing_name_gets_default(self):
        wb = {"sheets": [{"rows": []}]}
        result = workbook_sheet_order(wb)
        assert result == ["Sheet1"]


# --- workbook_numeric_summary tests ---

class TestWorkbookNumericSummary:

    def test_basic_numeric_stats(self):
        wb = _workbook([
            _sheet("Data", [
                _row([_cell(10, "float"), _cell(20, "float")]),
                _row([_cell(30, "float")]),
            ])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 3
        assert result["global_min"] == 10.0
        assert result["global_max"] == 30.0
        assert result["global_sum"] == 60.0

    def test_empty_workbook_numeric(self):
        wb = _workbook([_sheet("Empty", [])])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 0
        assert result["global_min"] is None
        assert result["global_max"] is None
        assert result["global_sum"] == 0

    def test_mixed_types_only_counts_numeric(self):
        wb = _workbook([
            _sheet("Mix", [
                _row([
                    _cell("hello", "string"),
                    _cell(42, "float"),
                    _cell(None, ""),
                ]),
            ])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 1
        assert result["global_sum"] == 42.0

    def test_per_sheet_stats(self):
        wb = _workbook([
            _sheet("A", [_row([_cell(5, "float")])]),
            _sheet("B", [_row([_cell(15, "int")])]),
        ])
        result = workbook_numeric_summary(wb)
        assert len(result["per_sheet"]) == 2
        assert result["per_sheet"][0]["sheet_name"] == "A"
        assert result["per_sheet"][0]["numeric_count"] == 1
        assert result["per_sheet"][1]["sheet_name"] == "B"
        assert result["per_sheet"][1]["numeric_count"] == 1

    def test_int_type_counted(self):
        wb = _workbook([
            _sheet("Ints", [_row([_cell(7, "int"), _cell(3, "int")])])
        ])
        result = workbook_numeric_summary(wb)
        assert result["total_numeric_cells"] == 2
        assert result["global_sum"] == 10.0


# --- workbook_column_count tests ---

class TestWorkbookColumnCount:

    def test_single_sheet_column_count(self):
        wb = _workbook([
            _sheet("S1", [
                _row([_cell("a"), _cell("b"), _cell("c")]),
                _row([_cell("d")]),
            ])
        ])
        result = workbook_column_count(wb)
        assert "per_sheet" in result
        assert result["per_sheet"][0]["max_columns"] == 3

    def test_empty_sheet(self):
        wb = _workbook([_sheet("Empty", [])])
        result = workbook_column_count(wb)
        assert result["per_sheet"][0]["max_columns"] == 0

    def test_multiple_sheets(self):
        wb = _workbook([
            _sheet("Wide", [_row([_cell("a"), _cell("b"), _cell("c"), _cell("d"), _cell("e")])]),
            _sheet("Narrow", [_row([_cell("x")])]),
        ])
        result = workbook_column_count(wb)
        assert len(result["per_sheet"]) == 2
        assert result["per_sheet"][0]["max_columns"] == 5
        assert result["per_sheet"][1]["max_columns"] == 1
