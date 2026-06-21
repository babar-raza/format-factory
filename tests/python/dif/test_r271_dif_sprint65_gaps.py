"""Tests for DIF Sprint 65 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_ROW_CELL-001   (Dif Row Cell Count Avg)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_row_cell_count_avg

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifRowCellCountAvg:
    def test_return_type(self):
        assert isinstance(dif_row_cell_count_avg(_MINIMAL), (int, float))

    def test_exact_8_for_minimal(self):
        assert dif_row_cell_count_avg(_MINIMAL) == 8.0

    def test_exact_3_for_numeric(self):
        assert dif_row_cell_count_avg(_NUMERIC) == 3.0

    def test_exact_1_for_single(self):
        assert dif_row_cell_count_avg(_SINGLE) == 1.0

    def test_positive(self):
        assert dif_row_cell_count_avg(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_row_cell_count_avg(_MINIMAL) == dif_row_cell_count_avg(_MINIMAL)
