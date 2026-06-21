"""Tests for PBM Sprint 57 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_EDGE_BLA-001   (Pbm Edge Black Count)
  GAP-PBM-FOSS-PBM_GRID_DEN-001   (Pbm Grid Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_edge_black_count, pbm_grid_density

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_DIR / "1x1-black.pbm")
_2X2 = str(_DIR / "2x2-checker.pbm")
_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmEdgeBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_edge_black_count(_1X1), int)

    def test_exact_1_for_1x1(self):
        assert pbm_edge_black_count(_1X1) == 1

    def test_exact_2_for_2x2(self):
        assert pbm_edge_black_count(_2X2) == 2

    def test_exact_3_for_3x2(self):
        assert pbm_edge_black_count(_3X2) == 3

    def test_nonnegative(self):
        assert pbm_edge_black_count(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pbm_edge_black_count(_1X1) == pbm_edge_black_count(_1X1)


class TestPbmGridDensity:
    def test_return_type(self):
        assert isinstance(pbm_grid_density(_1X1), (int, float))

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_grid_density(_1X1) == 1.0

    def test_exact_0_5_for_2x2_checker(self):
        assert pbm_grid_density(_2X2) == 0.5

    def test_exact_0_5_for_3x2_pattern(self):
        assert pbm_grid_density(_3X2) == 0.5

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_grid_density(_1X1) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_grid_density(_1X1) == pbm_grid_density(_1X1)
