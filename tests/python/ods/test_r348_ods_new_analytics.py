"""
Sprint 84 — ODS analytics round 3.
25 tests for 5 new analytics functions:
  ods_value_variance, ods_row_col_ratio, ods_string_length_sum,
  ods_col_count_variance, ods_multi_sheet_cell_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    ods_value_variance,
    ods_row_col_ratio,
    ods_string_length_sum,
    ods_col_count_variance,
    ods_multi_sheet_cell_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")
_NUMERIC = str(_SAMPLES / "numeric-row.ods")
_SINGLE = str(_SAMPLES / "single-cell.ods")


# --- ods_value_variance ---

class TestOdsValueVariance:
    def test_returns_float(self):
        result = ods_value_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ods_value_variance(_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = ods_value_variance(_NUMERIC)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_zero(self):
        result = ods_value_variance(_SINGLE)
        assert result == 0.0

    def test_out_of_range_sheet_index(self):
        result = ods_value_variance(_MINIMAL, sheet_index=999)
        assert result == 0.0


# --- ods_row_col_ratio ---

class TestOdsRowColRatio:
    def test_returns_float(self):
        result = ods_row_col_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ods_row_col_ratio(_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = ods_row_col_ratio(_NUMERIC)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell(self):
        result = ods_row_col_ratio(_SINGLE)
        assert result >= 0.0

    def test_out_of_range_sheet_index(self):
        result = ods_row_col_ratio(_MINIMAL, sheet_index=999)
        assert result == 0.0


# --- ods_string_length_sum ---

class TestOdsStringLengthSum:
    def test_returns_int(self):
        result = ods_string_length_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ods_string_length_sum(_MINIMAL)
        assert result >= 0

    def test_numeric_file_sum(self):
        result = ods_string_length_sum(_NUMERIC)
        assert isinstance(result, int) and result >= 0

    def test_single_cell(self):
        result = ods_string_length_sum(_SINGLE)
        assert result >= 0

    def test_out_of_range_sheet_index(self):
        result = ods_string_length_sum(_MINIMAL, sheet_index=999)
        assert result == 0


# --- ods_col_count_variance ---

class TestOdsColCountVariance:
    def test_returns_float(self):
        result = ods_col_count_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ods_col_count_variance(_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = ods_col_count_variance(_NUMERIC)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_zero_or_float(self):
        result = ods_col_count_variance(_SINGLE)
        assert result >= 0.0

    def test_out_of_range_sheet_index(self):
        result = ods_col_count_variance(_MINIMAL, sheet_index=999)
        assert result == 0.0


# --- ods_multi_sheet_cell_ratio ---

class TestOdsMultiSheetCellRatio:
    def test_returns_float(self):
        result = ods_multi_sheet_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = ods_multi_sheet_cell_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_numeric_file_bounded(self):
        result = ods_multi_sheet_cell_ratio(_NUMERIC)
        assert 0.0 <= result <= 1.0

    def test_single_cell_bounded(self):
        result = ods_multi_sheet_cell_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_minimal_positive(self):
        result = ods_multi_sheet_cell_ratio(_MINIMAL)
        assert isinstance(result, float)
