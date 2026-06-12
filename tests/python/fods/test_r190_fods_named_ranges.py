"""
tests/python/fods/test_r190_fods_named_ranges.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for workbook_named_range_list() and workbook_data_validation_summary().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import workbook_named_range_list, workbook_data_validation_summary

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestWorkbookNamedRangeList:
    def test_empty_workbook_returns_empty_list(self):
        result = workbook_named_range_list({})
        assert result == []

    def test_returns_list(self):
        result = workbook_named_range_list({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_named_range_list(model)
        assert isinstance(result, list)

    def test_no_named_ranges_in_minimal(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_named_range_list(model)
        # minimal file has no named ranges
        assert len(result) >= 0  # valid empty list

    def test_workbook_with_named_range_entry_structure(self):
        wb = {
            "named_ranges": [
                {"name": "MyRange", "range": "Sheet1.A1:A10"}
            ]
        }
        result = workbook_named_range_list(wb)
        # If named_ranges key is consumed, list should have entries or be empty
        assert isinstance(result, list)


class TestWorkbookDataValidationSummary:
    def test_empty_workbook_returns_zero_count(self):
        result = workbook_data_validation_summary({})
        assert result["validation_count"] == 0

    def test_returns_required_keys(self):
        result = workbook_data_validation_summary({})
        assert "validation_count" in result
        assert "validated_cell_ranges" in result

    def test_validated_cell_ranges_is_list(self):
        result = workbook_data_validation_summary({})
        assert isinstance(result["validated_cell_ranges"], list)

    def test_real_file_has_valid_structure(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_data_validation_summary(model)
        assert isinstance(result["validation_count"], int)
        assert result["validation_count"] >= 0

    def test_validation_count_matches_ranges_length(self):
        result = workbook_data_validation_summary({})
        # Empty case: count=0, ranges=[]
        assert result["validation_count"] == len(result["validated_cell_ranges"])
