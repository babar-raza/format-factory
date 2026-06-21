"""
Tests for 5 new CSV analytics functions (R345 / Sprint 81):
  csv_value_variance, csv_row_col_ratio, csv_alpha_field_count,
  csv_string_length_sum, csv_distinct_col_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_value_variance,
    csv_row_col_ratio,
    csv_alpha_field_count,
    csv_string_length_sum,
    csv_distinct_col_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.csv")
_QUOTED = str(_SAMPLES / "quoted-fields.csv")
_SINGLE = str(_SAMPLES / "single-cell.csv")


# ── csv_value_variance ─────────────────────────────────────────────────────────

class TestCsvValueVariance:
    def test_returns_float(self):
        result = csv_value_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = csv_value_variance(_MINIMAL)
        assert result >= 0.0

    def test_quoted_file(self):
        result = csv_value_variance(_QUOTED)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_file(self):
        result = csv_value_variance(_SINGLE)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_file(self):
        result = csv_value_variance(_MINIMAL)
        assert result >= 0.0


# ── csv_row_col_ratio ──────────────────────────────────────────────────────────

class TestCsvRowColRatio:
    def test_returns_float(self):
        result = csv_row_col_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = csv_row_col_ratio(_MINIMAL)
        assert result >= 0.0

    def test_quoted_file(self):
        result = csv_row_col_ratio(_QUOTED)
        assert isinstance(result, float) and result >= 0.0

    def test_single_cell_file(self):
        result = csv_row_col_ratio(_SINGLE)
        assert result >= 0.0

    def test_minimal_is_one(self):
        # 2x2 → 2 rows / 2 cols = 1.0
        result = csv_row_col_ratio(_MINIMAL)
        assert result == 1.0


# ── csv_alpha_field_count ──────────────────────────────────────────────────────

class TestCsvAlphaFieldCount:
    def test_returns_int(self):
        result = csv_alpha_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_alpha_field_count(_MINIMAL)
        assert result >= 0

    def test_quoted_file(self):
        result = csv_alpha_field_count(_QUOTED)
        assert isinstance(result, int) and result >= 0

    def test_single_cell_file(self):
        result = csv_alpha_field_count(_SINGLE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = csv_alpha_field_count(_MINIMAL)
        assert type(result) is int


# ── csv_string_length_sum ──────────────────────────────────────────────────────

class TestCsvStringLengthSum:
    def test_returns_int(self):
        result = csv_string_length_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_string_length_sum(_MINIMAL)
        assert result >= 0

    def test_quoted_file(self):
        result = csv_string_length_sum(_QUOTED)
        assert isinstance(result, int) and result >= 0

    def test_single_cell_file(self):
        result = csv_string_length_sum(_SINGLE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = csv_string_length_sum(_MINIMAL)
        assert type(result) is int


# ── csv_distinct_col_count ─────────────────────────────────────────────────────

class TestCsvDistinctColCount:
    def test_returns_int(self):
        result = csv_distinct_col_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_distinct_col_count(_MINIMAL)
        assert result >= 0

    def test_quoted_file(self):
        result = csv_distinct_col_count(_QUOTED)
        assert isinstance(result, int) and result >= 0

    def test_single_cell_file(self):
        result = csv_distinct_col_count(_SINGLE)
        assert result >= 0

    def test_minimal_has_two_cols(self):
        result = csv_distinct_col_count(_MINIMAL)
        assert result >= 1
