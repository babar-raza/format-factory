"""Tests for pbm_max_dimension and pbm_diagonal (Sprint 39).

Closes:
  GAP-PBM-FOSS-PBM_MAX_DIME-001  (Pbm Max Dimension)
  GAP-PBM-FOSS-PBM_DIAGONAL-001  (Pbm Diagonal)
"""
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_diagonal, pbm_max_dimension

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECK = str(_DIR / "2x2-checker.pbm")
_3X2_PAT = str(_DIR / "3x2-pattern.pbm")


class TestPbmMaxDimension:
    def test_return_type(self):
        assert isinstance(pbm_max_dimension(_1X1_BLACK), int)

    def test_exact_1_for_1x1(self):
        assert pbm_max_dimension(_1X1_BLACK) == 1

    def test_exact_2_for_2x2(self):
        assert pbm_max_dimension(_2X2_CHECK) == 2

    def test_exact_3_for_3x2(self):
        # max(3, 2) = 3
        assert pbm_max_dimension(_3X2_PAT) == 3

    def test_nonnegative(self):
        assert pbm_max_dimension(_1X1_BLACK) >= 1

    def test_consistent_across_calls(self):
        assert pbm_max_dimension(_1X1_BLACK) == pbm_max_dimension(_1X1_BLACK)


class TestPbmDiagonal:
    def test_return_type(self):
        assert isinstance(pbm_diagonal(_1X1_BLACK), float)

    def test_approx_sqrt2_for_1x1(self):
        # sqrt(1^2 + 1^2) = sqrt(2) ≈ 1.414
        assert math.isclose(pbm_diagonal(_1X1_BLACK), math.sqrt(2), rel_tol=1e-6)

    def test_approx_2sqrt2_for_2x2(self):
        # sqrt(2^2 + 2^2) = sqrt(8) ≈ 2.828
        assert math.isclose(pbm_diagonal(_2X2_CHECK), math.sqrt(8), rel_tol=1e-6)

    def test_approx_sqrt13_for_3x2(self):
        # sqrt(3^2 + 2^2) = sqrt(13) ≈ 3.606
        assert math.isclose(pbm_diagonal(_3X2_PAT), math.sqrt(13), rel_tol=1e-6)

    def test_positive(self):
        assert pbm_diagonal(_1X1_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_diagonal(_1X1_BLACK) == pbm_diagonal(_1X1_BLACK)
