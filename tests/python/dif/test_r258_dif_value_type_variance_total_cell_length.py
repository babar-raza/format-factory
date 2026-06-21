"""Tests for DIF gap closure batch 2 (Sprint 40).

Closes:
  GAP-DIF-FOSS-DIF_VALUE_TY-001   (Dif Value Type Variance)
  GAP-DIF-FOSS-DIF_TOTAL_CE-001   (Dif Total Cell Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_total_cell_length, dif_value_type_variance

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")
_SINGLE_CELL = str(_DIR / "single-cell.dif")


class TestDifValueTypeVariance:
    def test_return_type(self):
        assert isinstance(dif_value_type_variance(_MINIMAL_2X2), float)

    def test_zero_for_minimal_2x2(self):
        assert dif_value_type_variance(_MINIMAL_2X2) == 0.0

    def test_zero_for_numeric_row(self):
        assert dif_value_type_variance(_NUMERIC_ROW) == 0.0

    def test_zero_for_single_cell(self):
        assert dif_value_type_variance(_SINGLE_CELL) == 0.0

    def test_nonnegative(self):
        assert dif_value_type_variance(_MINIMAL_2X2) >= 0.0

    def test_consistent_across_calls(self):
        assert dif_value_type_variance(_MINIMAL_2X2) == dif_value_type_variance(_MINIMAL_2X2)


class TestDifTotalCellLength:
    def test_return_type(self):
        assert isinstance(dif_total_cell_length(_MINIMAL_2X2), int)

    def test_exact_36_for_minimal_2x2(self):
        assert dif_total_cell_length(_MINIMAL_2X2) == 36

    def test_exact_9_for_numeric_row(self):
        assert dif_total_cell_length(_NUMERIC_ROW) == 9

    def test_exact_4_for_single_cell(self):
        assert dif_total_cell_length(_SINGLE_CELL) == 4

    def test_nonnegative(self):
        assert dif_total_cell_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_total_cell_length(_MINIMAL_2X2) == dif_total_cell_length(_MINIMAL_2X2)
