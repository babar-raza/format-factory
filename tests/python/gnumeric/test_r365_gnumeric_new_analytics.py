"""
Sprint 101 — Gnumeric analytics round 4.
25 tests for 5 new analytics functions:
  gnumeric_total_cell_count, gnumeric_max_cell_per_sheet, gnumeric_numeric_cell_ratio,
  gnumeric_sheet_count, gnumeric_avg_cells_per_sheet
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_total_cell_count,
    gnumeric_max_cell_per_sheet,
    gnumeric_numeric_cell_ratio,
    gnumeric_sheet_count,
    gnumeric_avg_cells_per_sheet,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")
_EMPTY = str(_SAMPLES / "empty-sheet.gnumeric")


# --- gnumeric_total_cell_count ---

class TestGnumericTotalCellCount:
    def test_returns_int(self):
        result = gnumeric_total_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = gnumeric_total_cell_count(_MINIMAL)
        assert result >= 0

    def test_multi_cell_positive(self):
        result = gnumeric_total_cell_count(_MULTI)
        assert result > 0

    def test_empty_sheet(self):
        result = gnumeric_total_cell_count(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_minimal_non_negative(self):
        result = gnumeric_total_cell_count(_MINIMAL)
        assert result >= 0


# --- gnumeric_max_cell_per_sheet ---

class TestGnumericMaxCellPerSheet:
    def test_returns_int(self):
        result = gnumeric_max_cell_per_sheet(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = gnumeric_max_cell_per_sheet(_MINIMAL)
        assert result >= 0

    def test_multi_cell_positive(self):
        result = gnumeric_max_cell_per_sheet(_MULTI)
        assert result > 0

    def test_empty_sheet(self):
        result = gnumeric_max_cell_per_sheet(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_lte_total_cell_count(self):
        mx = gnumeric_max_cell_per_sheet(_MULTI)
        total = gnumeric_total_cell_count(_MULTI)
        assert mx <= total


# --- gnumeric_numeric_cell_ratio ---

class TestGnumericNumericCellRatio:
    def test_returns_float(self):
        result = gnumeric_numeric_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = gnumeric_numeric_cell_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_cell_bounded(self):
        result = gnumeric_numeric_cell_ratio(_MULTI)
        assert 0.0 <= result <= 1.0

    def test_empty_sheet(self):
        result = gnumeric_numeric_cell_ratio(_EMPTY)
        assert result == 0.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _MULTI, _EMPTY]:
            r = gnumeric_numeric_cell_ratio(path)
            assert 0.0 <= r <= 1.0


# --- gnumeric_sheet_count ---

class TestGnumericSheetCount:
    def test_returns_int(self):
        result = gnumeric_sheet_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = gnumeric_sheet_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = gnumeric_sheet_count(_MINIMAL)
        assert result >= 1

    def test_multi_cell_positive(self):
        result = gnumeric_sheet_count(_MULTI)
        assert result >= 1

    def test_empty_sheet_positive(self):
        result = gnumeric_sheet_count(_EMPTY)
        assert result >= 1


# --- gnumeric_avg_cells_per_sheet ---

class TestGnumericAvgCellsPerSheet:
    def test_returns_float(self):
        result = gnumeric_avg_cells_per_sheet(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = gnumeric_avg_cells_per_sheet(_MINIMAL)
        assert result >= 0.0

    def test_multi_cell_positive(self):
        result = gnumeric_avg_cells_per_sheet(_MULTI)
        assert result > 0.0

    def test_empty_sheet(self):
        result = gnumeric_avg_cells_per_sheet(_EMPTY)
        assert result == 0.0

    def test_consistent_with_total_and_sheet_count(self):
        total = gnumeric_total_cell_count(_MULTI)
        sheets = gnumeric_sheet_count(_MULTI)
        avg = gnumeric_avg_cells_per_sheet(_MULTI)
        assert abs(avg - total / sheets) < 0.001
