"""Tests for DIF Sprint 58 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_CELL_VAL-001   (Dif Cell Value Length Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_cell_value_length_sum

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifCellValueLengthSum:
    def test_return_type(self):
        assert isinstance(dif_cell_value_length_sum(_MINIMAL), int)

    def test_exact_342_for_minimal(self):
        assert dif_cell_value_length_sum(_MINIMAL) == 342

    def test_exact_120_for_numeric(self):
        assert dif_cell_value_length_sum(_NUMERIC) == 120

    def test_exact_41_for_single(self):
        assert dif_cell_value_length_sum(_SINGLE) == 41

    def test_positive(self):
        assert dif_cell_value_length_sum(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_cell_value_length_sum(_MINIMAL) == dif_cell_value_length_sum(_MINIMAL)
