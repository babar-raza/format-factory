"""
test_r75_fods_new_apis.py

R75 Train G: Tests for the two new FODS APIs:
- workbook_column_width_summary
- workbook_cell_type_matrix

Sprint: FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_column_width_summary,
    workbook_cell_type_matrix,
)


def _make_workbook(sheets=None):
    if sheets is None:
        sheets = []
    return {"sheets": sheets}


def _make_sheet(name, rows=None, columns=None):
    sheet = {"name": name, "rows": rows or [], "columns": columns or []}
    return sheet


def _make_row(cells):
    return {"cells": cells}


def _make_cell(value_type=None, value=None, formula=None):
    c: dict = {}
    if value_type:
        c["value_type"] = value_type
    if value is not None:
        c["value"] = value
    if formula is not None:
        c["formula"] = formula
    return c


class TestWorkbookColumnWidthSummary:
    """Tests for workbook_column_width_summary (R75)."""

    def test_empty_workbook_returns_empty(self):
        wb = _make_workbook()
        result = workbook_column_width_summary(wb)
        assert result == []

    def test_sheet_without_columns(self):
        wb = _make_workbook([_make_sheet("Sheet1")])
        result = workbook_column_width_summary(wb)
        assert len(result) == 1
        assert result[0]["sheet_name"] == "Sheet1"
        assert result[0]["column_count"] == 0
        assert result[0]["widths"] == []

    def test_columns_with_explicit_widths(self):
        cols = [
            {"column_width": "2.5cm"},
            {"column_width": "3.0cm"},
            {"column_width": None},
        ]
        wb = _make_workbook([_make_sheet("Data", columns=cols)])
        result = workbook_column_width_summary(wb)
        assert result[0]["column_count"] == 2
        assert result[0]["widths"] == ["2.5cm", "3.0cm", None]

    def test_style_column_width_key(self):
        cols = [{"style:column-width": "1.5in"}]
        wb = _make_workbook([_make_sheet("Sheet1", columns=cols)])
        result = workbook_column_width_summary(wb)
        assert result[0]["widths"] == ["1.5in"]
        assert result[0]["column_count"] == 1

    def test_multiple_sheets(self):
        wb = _make_workbook([
            _make_sheet("A", columns=[{"column_width": "2cm"}]),
            _make_sheet("B", columns=[{"column_width": "3cm"}, {"column_width": "4cm"}]),
        ])
        result = workbook_column_width_summary(wb)
        assert len(result) == 2
        assert result[0]["column_count"] == 1
        assert result[1]["column_count"] == 2

    def test_result_contains_sheet_name(self):
        wb = _make_workbook([_make_sheet("MySheet", columns=[{"width": "5cm"}])])
        result = workbook_column_width_summary(wb)
        assert result[0]["sheet_name"] == "MySheet"


class TestWorkbookCellTypeMatrix:
    """Tests for workbook_cell_type_matrix (R75)."""

    def test_empty_workbook_returns_empty(self):
        wb = _make_workbook()
        result = workbook_cell_type_matrix(wb)
        assert result == []

    def test_all_numeric_cells(self):
        rows = [_make_row([_make_cell("float"), _make_cell("float")])]
        wb = _make_workbook([_make_sheet("Sheet1", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"].get("numeric", 0) == 2
        assert result[0]["total_cells"] == 2

    def test_text_cells(self):
        rows = [_make_row([_make_cell("string"), _make_cell("text")])]
        wb = _make_workbook([_make_sheet("Sheet1", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"].get("text", 0) == 2

    def test_formula_cells(self):
        rows = [_make_row([_make_cell(formula="=A1+B1")])]
        wb = _make_workbook([_make_sheet("Sheet1", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"].get("formula", 0) == 1

    def test_empty_cells_not_in_total(self):
        rows = [_make_row([_make_cell(), _make_cell()])]
        wb = _make_workbook([_make_sheet("Sheet1", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["total_cells"] == 0

    def test_mixed_types(self):
        rows = [_make_row([
            _make_cell("float"),
            _make_cell("string"),
            _make_cell(formula="=SUM(A1)"),
            _make_cell("boolean"),
        ])]
        wb = _make_workbook([_make_sheet("Sheet1", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        by_type = result[0]["by_type"]
        assert by_type.get("numeric", 0) == 1
        assert by_type.get("text", 0) == 1
        assert by_type.get("formula", 0) == 1
        assert by_type.get("boolean", 0) == 1
        assert result[0]["total_cells"] == 4

    def test_returns_sheet_name(self):
        wb = _make_workbook([_make_sheet("Inventory")])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["sheet_name"] == "Inventory"

    def test_percentage_and_currency_counted_as_numeric(self):
        rows = [_make_row([_make_cell("percentage"), _make_cell("currency")])]
        wb = _make_workbook([_make_sheet("Prices", rows=rows)])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"].get("numeric", 0) == 2
