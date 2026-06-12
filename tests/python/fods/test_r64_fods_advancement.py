"""
test_r64_fods_advancement.py -- R64 Train H: FODS product advancement.

New capabilities added in R64:
1. workbook_row_style_summary(workbook) -- row style attributes per sheet
2. workbook_formula_edit_policy(workbook) -- formula edit/lock policy counts

These extend R63 capabilities (workbook_numeric_summary, workbook_column_count)
with row-level style inventory and formula protection analysis.

R64 Sprint: Train H -- FODS product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_row_style_summary,
    workbook_formula_edit_policy,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_workbook(sheets_data: list) -> dict:
    """Build a minimal workbook for testing."""
    sheets = []
    for item in sheets_data:
        sheet_name = item["name"]
        rows = []
        for row_data in item.get("rows", []):
            row = dict(row_data)  # copy
            if "cells" not in row:
                row["cells"] = []
            rows.append(row)
        sheets.append({"name": sheet_name, "rows": rows})
    return {"sheets": sheets, "warnings": [], "unsupported_features": [], "parse_errors": []}


# ---------------------------------------------------------------------------
# workbook_row_style_summary tests
# ---------------------------------------------------------------------------

class TestWorkbookRowStyleSummary:
    """Tests for workbook_row_style_summary()."""

    def test_empty_workbook(self):
        wb = {"sheets": [], "warnings": []}
        result = workbook_row_style_summary(wb)
        assert result == {}

    def test_no_styled_rows(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [{"cells": [{"value": 1}]}, {"cells": [{"value": 2}]}],
        }])
        result = workbook_row_style_summary(wb)
        assert result == {"Sheet1": []}

    def test_rows_with_style_attribute(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [
                {"cells": [], "style": "bold-row"},
                {"cells": []},
                {"cells": [], "style": "italic-row"},
            ],
        }])
        result = workbook_row_style_summary(wb)
        assert result["Sheet1"] == ["bold-row", "italic-row"]

    def test_rows_with_table_style_name(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [{"cells": [], "table:style-name": "ro1"}],
        }])
        result = workbook_row_style_summary(wb)
        assert result["Sheet1"] == ["ro1"]

    def test_rows_with_style_name_key(self):
        wb = _make_workbook([{
            "name": "Sheet1",
            "rows": [{"cells": [], "style_name": "alternate"}],
        }])
        result = workbook_row_style_summary(wb)
        assert result["Sheet1"] == ["alternate"]

    def test_multiple_sheets(self):
        wb = _make_workbook([
            {"name": "A", "rows": [{"cells": [], "style": "s1"}]},
            {"name": "B", "rows": [{"cells": []}]},
        ])
        result = workbook_row_style_summary(wb)
        assert result["A"] == ["s1"]
        assert result["B"] == []

    def test_returns_dict_keyed_by_sheet_name(self):
        wb = _make_workbook([{"name": "Data", "rows": []}])
        result = workbook_row_style_summary(wb)
        assert isinstance(result, dict)
        assert "Data" in result

    def test_api_accessible_from_package(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_row_style_summary")
        assert callable(fods.workbook_row_style_summary)


# ---------------------------------------------------------------------------
# workbook_formula_edit_policy tests
# ---------------------------------------------------------------------------

class TestWorkbookFormulaEditPolicy:
    """Tests for workbook_formula_edit_policy()."""

    def test_no_formulas(self):
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [{"value": 1}, {"value": 2}]}
        ]}]}
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 0
        assert result["editable_formulas"] == 0
        assert result["locked_formulas"] == 0
        assert result["policy"] == "no_formulas"

    def test_all_editable_formulas(self):
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [
                {"value": 3, "formula": "=A1+A2"},
                {"value": 5, "formula": "=SUM(A1:A3)"},
            ]}
        ]}]}
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 2
        assert result["editable_formulas"] == 2
        assert result["locked_formulas"] == 0
        assert result["policy"] == "all_editable"

    def test_locked_formulas(self):
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [
                {"value": 3, "formula": "=A1", "protected": True},
                {"value": 5, "formula": "=B1"},
            ]}
        ]}]}
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 2
        assert result["locked_formulas"] == 1
        assert result["editable_formulas"] == 1
        assert result["policy"] == "mixed"

    def test_all_locked_formulas(self):
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [
                {"value": 1, "formula": "=X", "protected": True},
                {"value": 2, "formula": "=Y", "table:protected": True},
            ]}
        ]}]}
        result = workbook_formula_edit_policy(wb)
        assert result["policy"] == "all_locked"
        assert result["locked_formulas"] == 2
        assert result["editable_formulas"] == 0

    def test_empty_workbook(self):
        wb = {"sheets": []}
        result = workbook_formula_edit_policy(wb)
        assert result["policy"] == "no_formulas"

    def test_mixed_formula_and_value_cells(self):
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [
                {"value": "text"},
                {"value": 10, "formula": "=SUM(A1:A5)"},
                {"value": None},
            ]}
        ]}]}
        result = workbook_formula_edit_policy(wb)
        assert result["total_formulas"] == 1

    def test_returns_correct_keys(self):
        wb = {"sheets": []}
        result = workbook_formula_edit_policy(wb)
        for key in ["total_formulas", "editable_formulas", "locked_formulas", "policy"]:
            assert key in result

    def test_api_accessible_from_package(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_formula_edit_policy")
        assert callable(fods.workbook_formula_edit_policy)
        assert "workbook_formula_edit_policy" in fods.__all__
