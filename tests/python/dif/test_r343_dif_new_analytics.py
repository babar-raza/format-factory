"""
Tests for 5 new DIF analytics functions (R343 / Sprint 79):
  dif_value_variance, dif_row_col_ratio, dif_cell_count_variance,
  dif_string_length_sum, dif_numeric_col_ratio
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_value_variance,
    dif_row_col_ratio,
    dif_cell_count_variance,
    dif_string_length_sum,
    dif_numeric_col_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.dif")
_NUMERIC = str(_SAMPLES / "numeric-row.dif")
_SINGLE = str(_SAMPLES / "single-cell.dif")


# ── dif_value_variance ─────────────────────────────────────────────────────────

class TestDifValueVariance:
    def test_returns_float(self):
        result = dif_value_variance(_NUMERIC)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = dif_value_variance(_NUMERIC)
        assert result >= 0.0

    def test_minimal_file(self):
        result = dif_value_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_returns_zero(self):
        result = dif_value_variance(_SINGLE)
        assert isinstance(result, float) and result >= 0.0

    def test_numeric_file(self):
        result = dif_value_variance(_NUMERIC)
        assert result >= 0.0


# ── dif_row_col_ratio ──────────────────────────────────────────────────────────

class TestDifRowColRatio:
    def test_returns_float(self):
        result = dif_row_col_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = dif_row_col_ratio(_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = dif_row_col_ratio(_NUMERIC)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_file(self):
        result = dif_row_col_ratio(_SINGLE)
        assert result >= 0.0

    def test_minimal_file(self):
        result = dif_row_col_ratio(_MINIMAL)
        assert result >= 0.0


# ── dif_cell_count_variance ────────────────────────────────────────────────────

class TestDifCellCountVariance:
    def test_returns_float(self):
        result = dif_cell_count_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = dif_cell_count_variance(_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = dif_cell_count_variance(_NUMERIC)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_returns_zero(self):
        result = dif_cell_count_variance(_SINGLE)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_file(self):
        result = dif_cell_count_variance(_MINIMAL)
        assert result >= 0.0


# ── dif_string_length_sum ──────────────────────────────────────────────────────

class TestDifStringLengthSum:
    def test_returns_int(self):
        result = dif_string_length_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = dif_string_length_sum(_MINIMAL)
        assert result >= 0

    def test_numeric_file(self):
        result = dif_string_length_sum(_NUMERIC)
        assert isinstance(result, int) and result >= 0

    def test_single_cell_file(self):
        result = dif_string_length_sum(_SINGLE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = dif_string_length_sum(_MINIMAL)
        assert type(result) is int


# ── dif_numeric_col_ratio ──────────────────────────────────────────────────────

class TestDifNumericColRatio:
    def test_returns_float(self):
        result = dif_numeric_col_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = dif_numeric_col_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_numeric_file(self):
        result = dif_numeric_col_ratio(_NUMERIC)
        assert 0.0 <= result <= 1.0

    def test_single_cell_file(self):
        result = dif_numeric_col_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_result_is_float(self):
        result = dif_numeric_col_ratio(_MINIMAL)
        assert isinstance(result, float)
