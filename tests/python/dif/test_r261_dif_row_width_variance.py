"""Tests for DIF Sprint 41 batch 2 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_ROW_WIDT-001  (Dif Row Width Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_row_width_variance

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")


class TestDifRowWidthVariance:
    def test_return_type(self):
        assert isinstance(dif_row_width_variance(_MINIMAL_2X2), float)

    def test_exact_0_0_for_minimal_2x2(self):
        assert dif_row_width_variance(_MINIMAL_2X2) == 0.0

    def test_exact_0_0_for_numeric_row(self):
        assert dif_row_width_variance(_NUMERIC_ROW) == 0.0

    def test_nonnegative(self):
        assert dif_row_width_variance(_MINIMAL_2X2) >= 0.0

    def test_consistent_across_calls(self):
        assert dif_row_width_variance(_MINIMAL_2X2) == dif_row_width_variance(_MINIMAL_2X2)
