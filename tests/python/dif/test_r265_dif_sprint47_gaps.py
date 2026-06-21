"""Tests for DIF Sprint 47 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_STRING_R-001  (Dif String Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_string_ratio

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifStringRatio:
    def test_return_type(self):
        assert isinstance(dif_string_ratio(_MINIMAL), (int, float))

    def test_exact_0_75_for_minimal(self):
        assert dif_string_ratio(_MINIMAL) == 0.75

    def test_zero_for_numeric_row(self):
        assert dif_string_ratio(_NUMERIC) == 0.0

    def test_zero_for_single_cell(self):
        assert dif_string_ratio(_SINGLE) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= dif_string_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert dif_string_ratio(_MINIMAL) == dif_string_ratio(_MINIMAL)
