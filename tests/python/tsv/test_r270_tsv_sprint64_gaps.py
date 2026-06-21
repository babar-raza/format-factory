"""Tests for TSV Sprint 64 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_VALUE_VA-001   (Tsv Value Variance)
  GAP-TSV-FOSS-TSV_ROW_COL_-001   (Tsv Row Col Ratio)
  GAP-TSV-FOSS-TSV_STRING_R-001   (Tsv String Ratio)
  GAP-TSV-FOSS-TSV_ALPHA_FI-001   (Tsv Alpha Field Count)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_value_variance, tsv_row_col_ratio, tsv_string_ratio, tsv_alpha_field_count

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvValueVariance:
    def test_return_type(self):
        assert isinstance(tsv_value_variance(_MINIMAL), (int, float))

    def test_exact_6_25_for_minimal(self):
        assert tsv_value_variance(_MINIMAL) == pytest.approx(6.25)

    def test_exact_1926_046875_for_multi(self):
        assert tsv_value_variance(_MULTI) == pytest.approx(1926.046875)

    def test_zero_for_single(self):
        assert tsv_value_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert tsv_value_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert tsv_value_variance(_MINIMAL) == tsv_value_variance(_MINIMAL)


class TestTsvRowColRatio:
    def test_return_type(self):
        assert isinstance(tsv_row_col_ratio(_MINIMAL), (int, float))

    def test_exact_1_0_for_minimal(self):
        assert tsv_row_col_ratio(_MINIMAL) == 1.0

    def test_exact_0_5_for_multi(self):
        assert tsv_row_col_ratio(_MULTI) == pytest.approx(0.5)

    def test_exact_1_0_for_single(self):
        assert tsv_row_col_ratio(_SINGLE) == 1.0

    def test_positive(self):
        assert tsv_row_col_ratio(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_row_col_ratio(_MINIMAL) == tsv_row_col_ratio(_MINIMAL)


class TestTsvStringRatio:
    def test_return_type(self):
        assert isinstance(tsv_string_ratio(_MINIMAL), (int, float))

    def test_exact_0_5_for_minimal(self):
        assert tsv_string_ratio(_MINIMAL) == pytest.approx(0.5)

    def test_exact_0_5_for_multi(self):
        assert tsv_string_ratio(_MULTI) == pytest.approx(0.5)

    def test_zero_for_single(self):
        assert tsv_string_ratio(_SINGLE) == 0.0

    def test_between_0_and_1(self):
        assert 0.0 <= tsv_string_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert tsv_string_ratio(_MINIMAL) == tsv_string_ratio(_MINIMAL)


class TestTsvAlphaFieldCount:
    def test_return_type(self):
        assert isinstance(tsv_alpha_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert tsv_alpha_field_count(_MINIMAL) == 2

    def test_exact_4_for_multi(self):
        assert tsv_alpha_field_count(_MULTI) == 4

    def test_zero_for_single(self):
        assert tsv_alpha_field_count(_SINGLE) == 0

    def test_nonnegative(self):
        assert tsv_alpha_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert tsv_alpha_field_count(_MINIMAL) == tsv_alpha_field_count(_MINIMAL)
