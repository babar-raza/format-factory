"""Tests for DIF Sprint 52 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_VALUE_SU-001   (Dif Value Sum)
  GAP-DIF-FOSS-DIF_AVG_STRI-001   (Dif Avg String Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_value_sum, dif_avg_string_length

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifValueSum:
    def test_return_type(self):
        assert isinstance(dif_value_sum(_MINIMAL), (int, float))

    def test_exact_141_for_minimal(self):
        assert dif_value_sum(_MINIMAL) == 141.0

    def test_exact_6_for_numeric_row(self):
        assert dif_value_sum(_NUMERIC) == 6.0

    def test_exact_42_for_single_cell(self):
        assert dif_value_sum(_SINGLE) == 42.0

    def test_nonnegative(self):
        assert dif_value_sum(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_value_sum(_MINIMAL) == dif_value_sum(_MINIMAL)


class TestDifAvgStringLength:
    def test_return_type(self):
        assert isinstance(dif_avg_string_length(_MINIMAL), (int, float))

    def test_positive_for_minimal(self):
        assert dif_avg_string_length(_MINIMAL) > 0

    def test_zero_for_numeric_row(self):
        assert dif_avg_string_length(_NUMERIC) == 0.0

    def test_zero_for_single_cell(self):
        assert dif_avg_string_length(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert dif_avg_string_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_avg_string_length(_MINIMAL) == dif_avg_string_length(_MINIMAL)
