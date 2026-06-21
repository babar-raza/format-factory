"""
Sprint 83 — Gnumeric analytics round 3.
25 tests for 5 new analytics functions:
  gnumeric_col_count_variance, gnumeric_avg_row_per_sheet,
  gnumeric_multi_sheet_ratio, gnumeric_fill_rate,
  gnumeric_string_cell_variance
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_col_count_variance,
    gnumeric_avg_row_per_sheet,
    gnumeric_multi_sheet_ratio,
    gnumeric_fill_rate,
    gnumeric_string_cell_variance,
)

_SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")
_EMPTY = str(_SAMPLES / "empty-sheet.gnumeric")


# --- gnumeric_col_count_variance ---

class TestGnumericColCountVariance:
    def test_returns_float(self):
        result = gnumeric_col_count_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = gnumeric_col_count_variance(_MINIMAL)
        assert result >= 0.0

    def test_single_sheet_is_zero(self):
        # Single sheet → variance is 0 by definition
        result = gnumeric_col_count_variance(_MINIMAL)
        assert result == 0.0

    def test_multi_cell(self):
        result = gnumeric_col_count_variance(_MULTI)
        assert isinstance(result, float) and result >= 0.0

    def test_empty_sheet(self):
        result = gnumeric_col_count_variance(_EMPTY)
        assert result == 0.0


# --- gnumeric_avg_row_per_sheet ---

class TestGnumericAvgRowPerSheet:
    def test_returns_float(self):
        result = gnumeric_avg_row_per_sheet(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = gnumeric_avg_row_per_sheet(_MINIMAL)
        assert result >= 0.0

    def test_multi_cell_positive(self):
        result = gnumeric_avg_row_per_sheet(_MULTI)
        assert result >= 0.0

    def test_empty_sheet_zero_or_float(self):
        result = gnumeric_avg_row_per_sheet(_EMPTY)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_at_most_rows(self):
        from src.python.gnumeric import gnumeric_total_row_count, gnumeric_sheet_count
        avg = gnumeric_avg_row_per_sheet(_MINIMAL)
        total = gnumeric_total_row_count(_MINIMAL)
        count = gnumeric_sheet_count(_MINIMAL)
        if count > 0:
            assert avg <= total


# --- gnumeric_multi_sheet_ratio ---

class TestGnumericMultiSheetRatio:
    def test_returns_float(self):
        result = gnumeric_multi_sheet_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = gnumeric_multi_sheet_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_cell_bounded(self):
        result = gnumeric_multi_sheet_ratio(_MULTI)
        assert 0.0 <= result <= 1.0

    def test_empty_sheet(self):
        result = gnumeric_multi_sheet_ratio(_EMPTY)
        assert isinstance(result, float)

    def test_consistent_with_sheet_count(self):
        from src.python.gnumeric import gnumeric_sheet_count
        ratio = gnumeric_multi_sheet_ratio(_MINIMAL)
        sc = gnumeric_sheet_count(_MINIMAL)
        if sc == 0:
            assert ratio == 0.0
        else:
            assert 0.0 <= ratio <= 1.0


# --- gnumeric_fill_rate ---

class TestGnumericFillRate:
    def test_returns_float(self):
        result = gnumeric_fill_rate(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = gnumeric_fill_rate(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_cell_positive(self):
        result = gnumeric_fill_rate(_MULTI)
        assert result >= 0.0

    def test_empty_sheet_zero(self):
        result = gnumeric_fill_rate(_EMPTY)
        assert result == 0.0

    def test_fill_rate_at_most_1(self):
        result = gnumeric_fill_rate(_MULTI)
        assert result <= 1.0


# --- gnumeric_string_cell_variance ---

class TestGnumericStringCellVariance:
    def test_returns_float(self):
        result = gnumeric_string_cell_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = gnumeric_string_cell_variance(_MINIMAL)
        assert result >= 0.0

    def test_single_sheet_is_zero(self):
        result = gnumeric_string_cell_variance(_MINIMAL)
        assert result == 0.0

    def test_multi_cell(self):
        result = gnumeric_string_cell_variance(_MULTI)
        assert isinstance(result, float) and result >= 0.0

    def test_empty_sheet(self):
        result = gnumeric_string_cell_variance(_EMPTY)
        assert result == 0.0
