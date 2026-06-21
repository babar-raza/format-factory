"""Tests for CSV Sprint 65 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_VALUE_VA-001   (Csv Value Variance)
  GAP-CSV-FOSS-CSV_ROW_COL_-001   (Csv Row Col Ratio)
  GAP-CSV-FOSS-CSV_ALPHA_FI-001   (Csv Alpha Field Count)
  GAP-CSV-FOSS-CSV_STRING_L-001   (Csv String Length Sum)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_value_variance, csv_row_col_ratio, csv_alpha_field_count, csv_string_length_sum

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvValueVariance:
    def test_return_type(self):
        assert isinstance(csv_value_variance(_MINIMAL), (int, float))

    def test_exact_6_25_for_minimal(self):
        assert csv_value_variance(_MINIMAL) == pytest.approx(6.25)

    def test_approx_25_for_quoted(self):
        assert csv_value_variance(_QUOTED) == pytest.approx(25.0, rel=1e-3)

    def test_zero_for_single(self):
        assert csv_value_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert csv_value_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert csv_value_variance(_MINIMAL) == csv_value_variance(_MINIMAL)


class TestCsvRowColRatio:
    def test_return_type(self):
        assert isinstance(csv_row_col_ratio(_MINIMAL), (int, float))

    def test_exact_1_0_for_minimal(self):
        assert csv_row_col_ratio(_MINIMAL) == 1.0

    def test_approx_0_667_for_quoted(self):
        assert csv_row_col_ratio(_QUOTED) == pytest.approx(0.6667, rel=1e-2)

    def test_exact_1_0_for_single(self):
        assert csv_row_col_ratio(_SINGLE) == 1.0

    def test_positive(self):
        assert csv_row_col_ratio(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert csv_row_col_ratio(_MINIMAL) == csv_row_col_ratio(_MINIMAL)


class TestCsvAlphaFieldCount:
    def test_return_type(self):
        assert isinstance(csv_alpha_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert csv_alpha_field_count(_MINIMAL) == 2

    def test_exact_4_for_quoted(self):
        assert csv_alpha_field_count(_QUOTED) == 4

    def test_zero_for_single(self):
        assert csv_alpha_field_count(_SINGLE) == 0

    def test_nonnegative(self):
        assert csv_alpha_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_alpha_field_count(_MINIMAL) == csv_alpha_field_count(_MINIMAL)


class TestCsvStringLengthSum:
    def test_return_type(self):
        assert isinstance(csv_string_length_sum(_MINIMAL), int)

    def test_exact_8_for_minimal(self):
        assert csv_string_length_sum(_MINIMAL) == 8

    def test_exact_52_for_quoted(self):
        assert csv_string_length_sum(_QUOTED) == 52

    def test_zero_for_single(self):
        assert csv_string_length_sum(_SINGLE) == 0

    def test_nonnegative(self):
        assert csv_string_length_sum(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_string_length_sum(_MINIMAL) == csv_string_length_sum(_MINIMAL)
