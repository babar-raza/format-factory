"""
Tests for 5 new TSV analytics functions (R344 / Sprint 80):
  tsv_value_variance, tsv_row_col_ratio, tsv_string_ratio,
  tsv_numeric_ratio, tsv_alpha_field_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv import (
    tsv_value_variance,
    tsv_row_col_ratio,
    tsv_string_ratio,
    tsv_numeric_ratio,
    tsv_alpha_field_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.tsv")
_MULTI = str(_SAMPLES / "multi-column.tsv")
_SINGLE = str(_SAMPLES / "single-cell.tsv")


# ── tsv_value_variance ─────────────────────────────────────────────────────────

class TestTsvValueVariance:
    def test_returns_float(self):
        result = tsv_value_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = tsv_value_variance(_MINIMAL)
        assert result >= 0.0

    def test_multi_column_file(self):
        result = tsv_value_variance(_MULTI)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_file(self):
        result = tsv_value_variance(_SINGLE)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_file(self):
        result = tsv_value_variance(_MINIMAL)
        assert result >= 0.0


# ── tsv_row_col_ratio ──────────────────────────────────────────────────────────

class TestTsvRowColRatio:
    def test_returns_float(self):
        result = tsv_row_col_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = tsv_row_col_ratio(_MINIMAL)
        assert result >= 0.0

    def test_multi_column_file(self):
        result = tsv_row_col_ratio(_MULTI)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_file(self):
        result = tsv_row_col_ratio(_SINGLE)
        assert result >= 0.0

    def test_minimal_file(self):
        result = tsv_row_col_ratio(_MINIMAL)
        assert result >= 0.0


# ── tsv_string_ratio ───────────────────────────────────────────────────────────

class TestTsvStringRatio:
    def test_returns_float(self):
        result = tsv_string_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = tsv_string_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_column_file(self):
        result = tsv_string_ratio(_MULTI)
        assert 0.0 <= result <= 1.0

    def test_single_cell_file(self):
        result = tsv_string_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_plus_numeric_ratio_bounded(self):
        s = tsv_string_ratio(_MINIMAL)
        n = tsv_numeric_ratio(_MINIMAL)
        assert abs(s + n - 1.0) < 1e-9 or (s == 0.0 and n == 0.0)


# ── tsv_numeric_ratio ──────────────────────────────────────────────────────────

class TestTsvNumericRatio:
    def test_returns_float(self):
        result = tsv_numeric_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = tsv_numeric_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_column_file(self):
        result = tsv_numeric_ratio(_MULTI)
        assert 0.0 <= result <= 1.0

    def test_single_cell_file(self):
        result = tsv_numeric_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_result_is_float(self):
        result = tsv_numeric_ratio(_MINIMAL)
        assert isinstance(result, float)


# ── tsv_alpha_field_count ──────────────────────────────────────────────────────

class TestTsvAlphaFieldCount:
    def test_returns_int(self):
        result = tsv_alpha_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_alpha_field_count(_MINIMAL)
        assert result >= 0

    def test_multi_column_file(self):
        result = tsv_alpha_field_count(_MULTI)
        assert isinstance(result, int) and result >= 0

    def test_single_cell_file(self):
        result = tsv_alpha_field_count(_SINGLE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = tsv_alpha_field_count(_MINIMAL)
        assert type(result) is int
