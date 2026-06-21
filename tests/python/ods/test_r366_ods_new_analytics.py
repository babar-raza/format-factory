"""
Sprint 102 — ODS analytics round 4.
25 tests for 5 new analytics functions:
  ods_total_cell_count, ods_max_row_length, ods_sheet_count,
  ods_numeric_cell_ratio, ods_avg_row_count_per_sheet
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    ods_total_cell_count,
    ods_max_row_length,
    ods_sheet_count,
    ods_numeric_cell_ratio,
    ods_avg_row_count_per_sheet,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")
_SINGLE = str(_SAMPLES / "single-cell.ods")
_NUMERIC = str(_SAMPLES / "numeric-row.ods")


# --- ods_total_cell_count ---

class TestOdsTotalCellCount:
    def test_returns_int(self):
        result = ods_total_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ods_total_cell_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = ods_total_cell_count(_MINIMAL)
        assert result > 0

    def test_single_cell_gte_one(self):
        result = ods_total_cell_count(_SINGLE)
        assert result >= 1

    def test_numeric_row_positive(self):
        result = ods_total_cell_count(_NUMERIC)
        assert result > 0


# --- ods_max_row_length ---

class TestOdsMaxRowLength:
    def test_returns_int(self):
        result = ods_max_row_length(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ods_max_row_length(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = ods_max_row_length(_MINIMAL)
        assert result > 0

    def test_single_cell_is_one(self):
        result = ods_max_row_length(_SINGLE)
        assert result >= 1

    def test_lte_total_cell_count(self):
        mx = ods_max_row_length(_NUMERIC)
        total = ods_total_cell_count(_NUMERIC)
        assert mx <= total


# --- ods_sheet_count ---

class TestOdsSheetCount:
    def test_returns_int(self):
        result = ods_sheet_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ods_sheet_count(_MINIMAL)
        assert result >= 0

    def test_minimal_gte_one(self):
        result = ods_sheet_count(_MINIMAL)
        assert result >= 1

    def test_single_cell_gte_one(self):
        result = ods_sheet_count(_SINGLE)
        assert result >= 1

    def test_numeric_row_gte_one(self):
        result = ods_sheet_count(_NUMERIC)
        assert result >= 1


# --- ods_numeric_cell_ratio ---

class TestOdsNumericCellRatio:
    def test_returns_float(self):
        result = ods_numeric_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = ods_numeric_cell_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_numeric_row_positive(self):
        result = ods_numeric_cell_ratio(_NUMERIC)
        assert result > 0.0

    def test_single_cell_bounded(self):
        result = ods_numeric_cell_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_out_of_range_sheet_zero(self):
        result = ods_numeric_cell_ratio(_MINIMAL, sheet_index=999)
        assert result == 0.0


# --- ods_avg_row_count_per_sheet ---

class TestOdsAvgRowCountPerSheet:
    def test_returns_float(self):
        result = ods_avg_row_count_per_sheet(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ods_avg_row_count_per_sheet(_MINIMAL)
        assert result >= 0.0

    def test_minimal_positive(self):
        result = ods_avg_row_count_per_sheet(_MINIMAL)
        assert result > 0.0

    def test_single_cell_is_one(self):
        result = ods_avg_row_count_per_sheet(_SINGLE)
        assert result >= 1.0

    def test_numeric_row_positive(self):
        result = ods_avg_row_count_per_sheet(_NUMERIC)
        assert result > 0.0
