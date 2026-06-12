"""
test_r66_fods_advancement.py -- R66 Train H: FODS product advancement.

New capabilities added in R66:
1. workbook_style_family_list(workbook)        -- style family inventory
2. workbook_data_validation_summary(workbook)  -- data validation summary

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train H -- FODS product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_style_family_list,
    workbook_data_validation_summary,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_workbook(**overrides) -> dict:
    """Build a minimal workbook for testing."""
    wb = {
        "sheets": [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    wb.update(overrides)
    return wb


# ---------------------------------------------------------------------------
# workbook_style_family_list tests
# ---------------------------------------------------------------------------

class TestWorkbookStyleFamilyList:
    """Tests for workbook_style_family_list()."""

    def test_empty_workbook_returns_empty_list(self):
        wb = _make_workbook()
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)
        assert result == []

    def test_returns_list_of_dicts(self):
        wb = _make_workbook(auto_styles=[
            {"family": "table-cell"},
            {"family": "table-cell"},
            {"family": "table"},
        ])
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)
        for item in result:
            assert "family_name" in item
            assert "style_count" in item

    def test_counts_families_from_auto_styles(self):
        wb = _make_workbook(auto_styles=[
            {"family": "table-cell"},
            {"family": "table-cell"},
            {"family": "table"},
        ])
        result = workbook_style_family_list(wb)
        by_name = {r["family_name"]: r["style_count"] for r in result}
        assert by_name["table-cell"] == 2
        assert by_name["table"] == 1

    def test_counts_families_from_styles_dict(self):
        wb = _make_workbook(styles={
            "paragraph": [{"name": "p1"}, {"name": "p2"}],
            "text": [{"name": "t1"}],
        })
        result = workbook_style_family_list(wb)
        by_name = {r["family_name"]: r["style_count"] for r in result}
        assert by_name["paragraph"] == 2
        assert by_name["text"] == 1

    def test_none_workbook_returns_empty(self):
        """Passing a workbook with no style keys returns empty list."""
        wb = _make_workbook()
        result = workbook_style_family_list(wb)
        assert result == []

    def test_style_family_attribute_variant(self):
        """Handles style:family attribute key."""
        wb = _make_workbook(auto_styles=[
            {"style:family": "graphic"},
        ])
        result = workbook_style_family_list(wb)
        assert len(result) == 1
        assert result[0]["family_name"] == "graphic"

    def test_results_sorted_by_family_name(self):
        wb = _make_workbook(auto_styles=[
            {"family": "zebra"},
            {"family": "alpha"},
        ])
        result = workbook_style_family_list(wb)
        names = [r["family_name"] for r in result]
        assert names == sorted(names)

    def test_missing_family_uses_unknown(self):
        wb = _make_workbook(auto_styles=[{}])
        result = workbook_style_family_list(wb)
        assert len(result) == 1
        assert result[0]["family_name"] == "unknown"


# ---------------------------------------------------------------------------
# workbook_data_validation_summary tests
# ---------------------------------------------------------------------------

class TestWorkbookDataValidationSummary:
    """Tests for workbook_data_validation_summary()."""

    def test_empty_workbook_returns_zero(self):
        wb = _make_workbook()
        result = workbook_data_validation_summary(wb)
        assert isinstance(result, dict)
        assert result["validation_count"] == 0
        assert result["validated_cell_ranges"] == []

    def test_returns_correct_keys(self):
        wb = _make_workbook()
        result = workbook_data_validation_summary(wb)
        assert "validation_count" in result
        assert "validated_cell_ranges" in result

    def test_counts_explicit_validations(self):
        wb = _make_workbook(data_validations=[
            {"cell_range": "Sheet1.A1:A10"},
            {"cell_range": "Sheet1.B1:B5"},
        ])
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 2
        assert len(result["validated_cell_ranges"]) == 2

    def test_cell_range_values_extracted(self):
        wb = _make_workbook(data_validations=[
            {"cell_range": "Sheet1.A1:A10"},
        ])
        result = workbook_data_validation_summary(wb)
        assert "Sheet1.A1:A10" in result["validated_cell_ranges"]

    def test_cell_level_validation_attributes(self):
        wb = _make_workbook(sheets=[
            {"name": "Sheet1", "rows": [
                {"cells": [
                    {"value": 1, "validation": "val1"},
                    {"value": 2, "validation": "val2"},
                ]},
            ]},
        ])
        result = workbook_data_validation_summary(wb)
        assert "val1" in result["validated_cell_ranges"]
        assert "val2" in result["validated_cell_ranges"]

    def test_none_data_validations_handled(self):
        wb = _make_workbook(data_validations=None)
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 0

    def test_empty_data_validations_list(self):
        wb = _make_workbook(data_validations=[])
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 0
        assert result["validated_cell_ranges"] == []


# ---------------------------------------------------------------------------
# API accessibility tests
# ---------------------------------------------------------------------------

class TestTrainHR66FodsApiAccess:
    """New R66 functions must be accessible from the fods package."""

    def test_workbook_style_family_list_callable(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_style_family_list")
        assert callable(fods.workbook_style_family_list)

    def test_workbook_data_validation_summary_callable(self):
        import src.python.fods as fods
        assert hasattr(fods, "workbook_data_validation_summary")
        assert callable(fods.workbook_data_validation_summary)

    def test_all_r66_new_apis_in_all(self):
        import src.python.fods as fods
        for api in ["workbook_style_family_list", "workbook_data_validation_summary"]:
            assert api in fods.__all__, f"{api} must be in fods.__all__"
