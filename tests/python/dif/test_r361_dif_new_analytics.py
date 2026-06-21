"""
Sprint 97 — DIF analytics round 4.
25 tests for 5 new analytics functions:
  dif_total_cell_count, dif_max_row_length, dif_numeric_cell_ratio,
  dif_row_count, dif_avg_cells_per_row
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_total_cell_count,
    dif_max_row_length,
    dif_numeric_cell_ratio,
    dif_row_count,
    dif_avg_cells_per_row,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.dif")
_SINGLE = str(_SAMPLES / "single-cell.dif")
_NUMERIC = str(_SAMPLES / "numeric-row.dif")


# --- dif_total_cell_count ---

class TestDifTotalCellCount:
    def test_returns_int(self):
        result = dif_total_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = dif_total_cell_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = dif_total_cell_count(_MINIMAL)
        assert result > 0

    def test_single_cell_is_one(self):
        result = dif_total_cell_count(_SINGLE)
        assert result >= 1

    def test_numeric_row_positive(self):
        result = dif_total_cell_count(_NUMERIC)
        assert result > 0


# --- dif_max_row_length ---

class TestDifMaxRowLength:
    def test_returns_int(self):
        result = dif_max_row_length(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = dif_max_row_length(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = dif_max_row_length(_MINIMAL)
        assert result > 0

    def test_single_cell_is_one(self):
        result = dif_max_row_length(_SINGLE)
        assert result >= 1

    def test_numeric_row_positive(self):
        result = dif_max_row_length(_NUMERIC)
        assert result > 0


# --- dif_numeric_cell_ratio ---

class TestDifNumericCellRatio:
    def test_returns_float(self):
        result = dif_numeric_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = dif_numeric_cell_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_numeric_row_positive(self):
        result = dif_numeric_cell_ratio(_NUMERIC)
        assert result > 0.0

    def test_single_cell_bounded(self):
        result = dif_numeric_cell_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            r = dif_numeric_cell_ratio(path)
            assert 0.0 <= r <= 1.0


# --- dif_row_count ---

class TestDifRowCount:
    def test_returns_int(self):
        result = dif_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = dif_row_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = dif_row_count(_MINIMAL)
        assert result > 0

    def test_single_cell(self):
        result = dif_row_count(_SINGLE)
        assert result >= 1

    def test_numeric_row_positive(self):
        result = dif_row_count(_NUMERIC)
        assert result > 0


# --- dif_avg_cells_per_row ---

class TestDifAvgCellsPerRow:
    def test_returns_float(self):
        result = dif_avg_cells_per_row(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = dif_avg_cells_per_row(_MINIMAL)
        assert result >= 0.0

    def test_minimal_positive(self):
        result = dif_avg_cells_per_row(_MINIMAL)
        assert result > 0.0

    def test_single_cell_is_one(self):
        result = dif_avg_cells_per_row(_SINGLE)
        assert result >= 1.0

    def test_numeric_row_positive(self):
        result = dif_avg_cells_per_row(_NUMERIC)
        assert result > 0.0
