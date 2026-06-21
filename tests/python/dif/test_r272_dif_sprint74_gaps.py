"""Tests for DIF Sprint 74 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_VALUE_TE-001   (Dif Value Text Total Length)
  GAP-DIF-FOSS-DIF_CELL_TEX-001   (Dif Cell Text Variance)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_value_text_total_length, dif_cell_text_variance

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifValueTextTotalLength:
    def test_return_type(self):
        assert isinstance(dif_value_text_total_length(_MINIMAL), int)

    def test_exact_342_for_minimal(self):
        assert dif_value_text_total_length(_MINIMAL) == 342

    def test_exact_120_for_numeric(self):
        assert dif_value_text_total_length(_NUMERIC) == 120

    def test_exact_41_for_single(self):
        assert dif_value_text_total_length(_SINGLE) == 41

    def test_positive(self):
        assert dif_value_text_total_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_value_text_total_length(_MINIMAL) == dif_value_text_total_length(_MINIMAL)


class TestDifCellTextVariance:
    def test_return_type(self):
        assert isinstance(dif_cell_text_variance(_MINIMAL), (int, float))

    def test_approx_8_19_for_minimal(self):
        assert dif_cell_text_variance(_MINIMAL) == pytest.approx(8.1875)

    def test_zero_for_numeric(self):
        assert dif_cell_text_variance(_NUMERIC) == 0.0

    def test_zero_for_single(self):
        assert dif_cell_text_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert dif_cell_text_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert dif_cell_text_variance(_MINIMAL) == dif_cell_text_variance(_MINIMAL)
