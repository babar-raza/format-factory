"""Tests for PGM brightness and geometry analytics (Sprint 39).

Closes:
  GAP-PGM-FOSS-PGM_HAS_ANY_-001  (Pgm Has Any Saturated)
  GAP-PGM-FOSS-PGM_IS_ALL_D-001  (Pgm Is All Dark)
  GAP-PGM-FOSS-PGM_PERIMETE-001  (Pgm Perimeter)
  GAP-PGM-FOSS-PGM_UNIQUE_V-001  (Pgm Unique Value Count)
  GAP-PGM-FOSS-PGM_DIMENSIO-001  (Pgm Dimension Ratio)
  GAP-PGM-FOSS-PGM_IS_SQUAR-001  (Pgm Is Square)
  GAP-PGM-FOSS-PGM_IS_LANDS-001  (Pgm Is Landscape)
  GAP-PGM-FOSS-PGM_MAX_DIME-001  (Pgm Max Dimension)
  GAP-PGM-FOSS-PGM_IS_ALL_B-001  (Pgm Is All Bright)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_dimension_ratio,
    pgm_has_any_saturated,
    pgm_is_all_bright,
    pgm_is_all_dark,
    pgm_is_landscape,
    pgm_is_square,
    pgm_max_dimension,
    pgm_perimeter,
    pgm_unique_value_count,
)

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")       # 1x1, value=255 (fully bright, saturated)
_2X2_GRAD = str(_DIR / "2x2-gradient.pgm")     # 2x2, 4 unique values (gradient)
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")         # 3x1 landscape, 3 unique values


class TestPgmHasAnySaturated:
    def test_return_type(self):
        assert isinstance(pgm_has_any_saturated(_1X1_WHITE), bool)

    def test_true_for_1x1_white(self):
        # value=255 is fully saturated
        assert pgm_has_any_saturated(_1X1_WHITE) is True

    def test_true_for_2x2_gradient(self):
        # gradient includes bright (saturated) pixels
        assert pgm_has_any_saturated(_2X2_GRAD) is True

    def test_true_for_3x1_ramp(self):
        # ramp includes 255
        assert pgm_has_any_saturated(_3X1_RAMP) is True

    def test_consistent_across_calls(self):
        assert pgm_has_any_saturated(_1X1_WHITE) == pgm_has_any_saturated(_1X1_WHITE)


class TestPgmIsAllDark:
    def test_return_type(self):
        assert isinstance(pgm_is_all_dark(_1X1_WHITE), bool)

    def test_false_for_1x1_white(self):
        # value=255 is not dark
        assert pgm_is_all_dark(_1X1_WHITE) is False

    def test_false_for_2x2_gradient(self):
        # has bright pixels -> not all dark
        assert pgm_is_all_dark(_2X2_GRAD) is False

    def test_false_for_3x1_ramp(self):
        assert pgm_is_all_dark(_3X1_RAMP) is False

    def test_consistent_across_calls(self):
        assert pgm_is_all_dark(_1X1_WHITE) == pgm_is_all_dark(_1X1_WHITE)


class TestPgmPerimeter:
    def test_return_type(self):
        assert isinstance(pgm_perimeter(_1X1_WHITE), int)

    def test_exact_4_for_1x1(self):
        assert pgm_perimeter(_1X1_WHITE) == 4

    def test_exact_8_for_2x2(self):
        assert pgm_perimeter(_2X2_GRAD) == 8

    def test_exact_8_for_3x1(self):
        # 2*(3+1) = 8
        assert pgm_perimeter(_3X1_RAMP) == 8

    def test_nonnegative(self):
        assert pgm_perimeter(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_perimeter(_1X1_WHITE) == pgm_perimeter(_1X1_WHITE)


class TestPgmUniqueValueCount:
    def test_return_type(self):
        assert isinstance(pgm_unique_value_count(_1X1_WHITE), int)

    def test_exact_1_for_1x1_white(self):
        # Single pixel value 255 -> 1 unique value
        assert pgm_unique_value_count(_1X1_WHITE) == 1

    def test_exact_4_for_2x2_gradient(self):
        # 2x2 gradient has 4 different values
        assert pgm_unique_value_count(_2X2_GRAD) == 4

    def test_exact_3_for_3x1_ramp(self):
        # 3 pixels with 3 unique values
        assert pgm_unique_value_count(_3X1_RAMP) == 3

    def test_nonnegative(self):
        assert pgm_unique_value_count(_1X1_WHITE) >= 1

    def test_consistent_across_calls(self):
        assert pgm_unique_value_count(_1X1_WHITE) == pgm_unique_value_count(_1X1_WHITE)


class TestPgmDimensionRatio:
    def test_return_type(self):
        assert isinstance(pgm_dimension_ratio(_1X1_WHITE), float)

    def test_exact_1_0_for_1x1(self):
        assert pgm_dimension_ratio(_1X1_WHITE) == 1.0

    def test_exact_1_0_for_2x2(self):
        assert pgm_dimension_ratio(_2X2_GRAD) == 1.0

    def test_exact_3_0_for_3x1(self):
        # 3/1 = 3.0
        assert pgm_dimension_ratio(_3X1_RAMP) == 3.0

    def test_positive(self):
        assert pgm_dimension_ratio(_1X1_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_dimension_ratio(_1X1_WHITE) == pgm_dimension_ratio(_1X1_WHITE)


class TestPgmIsSquare:
    def test_return_type(self):
        assert isinstance(pgm_is_square(_1X1_WHITE), bool)

    def test_true_for_1x1(self):
        assert pgm_is_square(_1X1_WHITE) is True

    def test_true_for_2x2(self):
        assert pgm_is_square(_2X2_GRAD) is True

    def test_false_for_3x1(self):
        assert pgm_is_square(_3X1_RAMP) is False

    def test_consistent_across_calls(self):
        assert pgm_is_square(_1X1_WHITE) == pgm_is_square(_1X1_WHITE)


class TestPgmIsLandscape:
    def test_return_type(self):
        assert isinstance(pgm_is_landscape(_1X1_WHITE), bool)

    def test_false_for_1x1_square(self):
        assert pgm_is_landscape(_1X1_WHITE) is False

    def test_false_for_2x2_square(self):
        assert pgm_is_landscape(_2X2_GRAD) is False

    def test_true_for_3x1(self):
        # 3 wide x 1 high: landscape
        assert pgm_is_landscape(_3X1_RAMP) is True

    def test_consistent_across_calls(self):
        assert pgm_is_landscape(_3X1_RAMP) == pgm_is_landscape(_3X1_RAMP)


class TestPgmMaxDimension:
    def test_return_type(self):
        assert isinstance(pgm_max_dimension(_1X1_WHITE), int)

    def test_exact_1_for_1x1(self):
        assert pgm_max_dimension(_1X1_WHITE) == 1

    def test_exact_2_for_2x2(self):
        assert pgm_max_dimension(_2X2_GRAD) == 2

    def test_exact_3_for_3x1(self):
        # max(3, 1) = 3
        assert pgm_max_dimension(_3X1_RAMP) == 3

    def test_nonnegative(self):
        assert pgm_max_dimension(_1X1_WHITE) >= 1

    def test_consistent_across_calls(self):
        assert pgm_max_dimension(_1X1_WHITE) == pgm_max_dimension(_1X1_WHITE)


class TestPgmIsAllBright:
    def test_return_type(self):
        assert isinstance(pgm_is_all_bright(_1X1_WHITE), bool)

    def test_true_for_1x1_white(self):
        # value=255 is fully bright
        assert pgm_is_all_bright(_1X1_WHITE) is True

    def test_false_for_2x2_gradient(self):
        # gradient has dark pixels -> not all bright
        assert pgm_is_all_bright(_2X2_GRAD) is False

    def test_false_for_3x1_ramp(self):
        # ramp starts at 0 -> not all bright
        assert pgm_is_all_bright(_3X1_RAMP) is False

    def test_consistent_across_calls(self):
        assert pgm_is_all_bright(_1X1_WHITE) == pgm_is_all_bright(_1X1_WHITE)
