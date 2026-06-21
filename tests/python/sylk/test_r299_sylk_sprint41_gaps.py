"""Tests for SYLK Sprint 41 gap closure.

Closes:
  GAP-SYLK-FOSS-SYLK_AVG_RO-001  (Sylk Avg Row Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_avg_row_density

_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.slk")
_NUMERIC_ROW = str(_DIR / "numeric-row.slk")
_SINGLE_CELL = str(_DIR / "single-cell.slk")


class TestSylkAvgRowDensity:
    def test_return_type(self):
        assert isinstance(sylk_avg_row_density(_MINIMAL_2X2), float)

    def test_exact_2_0_for_minimal_2x2(self):
        assert sylk_avg_row_density(_MINIMAL_2X2) == 2.0

    def test_exact_3_0_for_numeric_row(self):
        assert sylk_avg_row_density(_NUMERIC_ROW) == 3.0

    def test_exact_1_0_for_single_cell(self):
        assert sylk_avg_row_density(_SINGLE_CELL) == 1.0

    def test_positive(self):
        assert sylk_avg_row_density(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert sylk_avg_row_density(_MINIMAL_2X2) == sylk_avg_row_density(_MINIMAL_2X2)
