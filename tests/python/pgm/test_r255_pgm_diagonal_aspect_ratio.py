"""Tests for pgm_diagonal and pgm_aspect_ratio (Sprint 39).

Closes:
  GAP-PGM-FOSS-PGM_DIAGONAL-001  (Pgm Diagonal)
  GAP-PGM-FOSS-PGM_ASPECT_R-001  (Pgm Aspect Ratio)
"""
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_aspect_ratio, pgm_diagonal

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRAD = str(_DIR / "2x2-gradient.pgm")
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmDiagonal:
    def test_return_type(self):
        assert isinstance(pgm_diagonal(_1X1_WHITE), float)

    def test_approx_sqrt2_for_1x1(self):
        # sqrt(1^2 + 1^2) ≈ 1.414
        assert math.isclose(pgm_diagonal(_1X1_WHITE), math.sqrt(2), rel_tol=1e-6)

    def test_approx_2sqrt2_for_2x2(self):
        # sqrt(2^2 + 2^2) ≈ 2.828
        assert math.isclose(pgm_diagonal(_2X2_GRAD), math.sqrt(8), rel_tol=1e-6)

    def test_approx_sqrt10_for_3x1(self):
        # sqrt(3^2 + 1^2) = sqrt(10) ≈ 3.162
        assert math.isclose(pgm_diagonal(_3X1_RAMP), math.sqrt(10), rel_tol=1e-6)

    def test_positive(self):
        assert pgm_diagonal(_1X1_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_diagonal(_1X1_WHITE) == pgm_diagonal(_1X1_WHITE)


class TestPgmAspectRatio:
    def test_return_type(self):
        assert isinstance(pgm_aspect_ratio(_1X1_WHITE), float)

    def test_exact_1_0_for_1x1(self):
        # 1/1 = 1.0
        assert pgm_aspect_ratio(_1X1_WHITE) == 1.0

    def test_exact_1_0_for_2x2(self):
        # 2/2 = 1.0
        assert pgm_aspect_ratio(_2X2_GRAD) == 1.0

    def test_exact_3_0_for_3x1(self):
        # 3/1 = 3.0
        assert pgm_aspect_ratio(_3X1_RAMP) == 3.0

    def test_positive(self):
        assert pgm_aspect_ratio(_1X1_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_aspect_ratio(_1X1_WHITE) == pgm_aspect_ratio(_1X1_WHITE)
