"""
test_r65_fods_advancement.py -- R65 Train H: FODS product advancement.

New capabilities added in R65:
1. workbook_named_range_list(workbook) -- list of defined named ranges
2. workbook_column_style_summary(workbook) -- column style attributes per sheet

These extend R64 capabilities (workbook_row_style_summary, workbook_formula_edit_policy)
with named range inventory and column-level style metadata.

R65 Sprint: Train H -- FODS product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_named_range_list,
    workbook_column_style_summary,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_workbook(sheets_data: list, named_ranges: list | None = None) -> dict:
    """Build a minimal workbook for testing."""
    sheets = []
    for item in sheets_data:
        sheet = {"name": item["name"]}
        if "rows" in item:
            rows = []
            for row_data in item["rows"]:
                row = dict(row_data)
                if "cells" not in row:
                    row["cells"] = []
                rows.append(row)
            sheet["rows"] = rows
        else:
            sheet["rows"] = []
        if "columns" in item:
            sheet["columns"] = item["columns"]
        if "named_ranges" in item:
            sheet["named_ranges"] = item["named_ranges"]
        sheets.append(sheet)
    wb = {"sheets": sheets, "warnings": [], "unsupported_features": [], "parse_errors": []}
    if named_ranges is not None:
        wb["named_ranges"] = named_ranges
    return wb


# ---------------------------------------------------------------------------
# workbook_named_range_list tests
# ---------------------------------------------------------------------------

class TestWorkbookNamedRangeList:
    """Tests for workbook_named_range_list()."""

    def test_empty_workbook(self):
        wb = {"sheets": [], "warnings": []}
        result = workbook_named_range_list(wb)
        assert result == []

    def test_no_named_ranges(self):
        wb = _make_workbook([{"name": "Sheet1", "rows": [{"cells": [{"value": 1}]}]}])
        result = workbook_named_range_list(wb)
        assert result == []

    def test_workbook_level_named_ranges(self):
        wb = _make_workbook(
            [{"name": "Sheet1"}],
            named_ranges=[
                {"name": "SalesData", "cell_range": "Sheet1.A1:C10", "base_cell": "Sheet1.A1"},
            ],
        )
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "SalesData"
        assert result[0]["cell_range"] == "Sheet1.A1:C10"
        assert result[0]["base_cell"] == "Sheet1.A1"

    def test_odf_namespace_named_range(self):
        wb = _make_workbook(
            [{"name": "Sheet1"}],
            named_ranges=[
                {"table:name": "Budget", "table:cell-range-address": "Sheet1.B2:D5"},
            ],
        )
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "Budget"
        assert result[0]["cell_range"] == "Sheet1.B2:D5"

    def test_sheet_level_named_ranges(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "named_ranges": [{"name": "LocalRange", "cell_range": "A1:A5"}],
        }])
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "LocalRange"

    def test_multiple_named_ranges(self):
        wb = _make_workbook(
            [{"name": "S1"}],
            named_ranges=[
                {"name": "Range1", "cell_range": "S1.A1:A5"},
                {"name": "Range2", "cell_range": "S1.B1:B5"},
                {"name": "Range3", "cell_range": "S1.C1:C5"},
            ],
        )
        result = workbook_named_range_list(wb)
        assert len(result) == 3
        assert [r["name"] for r in result] == ["Range1", "Range2", "Range3"]

    def test_string_named_range(self):
        wb = _make_workbook([{"name": "S1"}], named_ranges=["SimpleRange"])
        result = workbook_named_range_list(wb)
        assert len(result) == 1
        assert result[0]["name"] == "SimpleRange"

    def test_api_accessible_from_package(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_named_range_list")
        assert callable(fods.workbook_named_range_list)
        assert "workbook_named_range_list" in fods.__all__


# ---------------------------------------------------------------------------
# workbook_column_style_summary tests
# ---------------------------------------------------------------------------

class TestWorkbookColumnStyleSummary:
    """Tests for workbook_column_style_summary()."""

    def test_empty_workbook(self):
        wb = {"sheets": [], "warnings": []}
        result = workbook_column_style_summary(wb)
        assert result == {}

    def test_no_styled_columns(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [{"cells": [{"value": 1}]}],
        }])
        result = workbook_column_style_summary(wb)
        assert result == {"Sheet1": []}

    def test_columns_with_style_attribute(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "columns": [
                {"style": "co1"},
                {"style": "co2"},
            ],
        }])
        result = workbook_column_style_summary(wb)
        assert result["Sheet1"] == ["co1", "co2"]

    def test_columns_with_table_style_name(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "columns": [{"table:style-name": "narrow-col"}],
        }])
        result = workbook_column_style_summary(wb)
        assert result["Sheet1"] == ["narrow-col"]

    def test_columns_with_style_name_key(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "columns": [{"style_name": "wide"}],
        }])
        result = workbook_column_style_summary(wb)
        assert result["Sheet1"] == ["wide"]

    def test_fallback_to_first_row_column_style(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [{"cells": [
                {"value": 1, "column_style": "fallback-style"},
            ]}],
        }])
        result = workbook_column_style_summary(wb)
        assert result["Sheet1"] == ["fallback-style"]

    def test_multiple_sheets(self):
        wb = _make_workbook([
            {"name": "A", "columns": [{"style": "s1"}]},
            {"name": "B", "rows": [{"cells": []}]},
        ])
        result = workbook_column_style_summary(wb)
        assert result["A"] == ["s1"]
        assert result["B"] == []

    def test_api_accessible_from_package(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_column_style_summary")
        assert callable(fods.workbook_column_style_summary)
        assert "workbook_column_style_summary" in fods.__all__
