"""Tests for ppm_perimeter, ppm_dimension_ratio, ppm_is_square, ppm_is_landscape,
ppm_max_dimension, ppm_has_pure_black, ppm_max_channel_sum (Sprint 39).

Closes:
  GAP-PPM-FOSS-PPM_PERIMETE-001  (Ppm Perimeter)
  GAP-PPM-FOSS-PPM_DIMENSIO-001  (Ppm Dimension Ratio)
  GAP-PPM-FOSS-PPM_IS_SQUAR-001  (Ppm Is Square)
  GAP-PPM-FOSS-PPM_IS_LANDS-001  (Ppm Is Landscape)
  GAP-PPM-FOSS-PPM_MAX_DIME-001  (Ppm Max Dimension)
  GAP-PPM-FOSS-PPM_HAS_PURE-001  (Ppm Has Pure Black)
  GAP-PPM-FOSS-PPM_MAX_CHAN-001  (Ppm Max Channel Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_dimension_ratio,
    ppm_has_pure_black,
    ppm_is_landscape,
    ppm_is_square,
    ppm_max_channel_sum,
    ppm_max_dimension,
    ppm_perimeter,
)

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")           # 1x1 square, red (255,0,0)
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")         # 2x2 square, RGBW corners
_3X1_GRAD = str(_DIR / "3x1-gradient.ppm")     # 3 wide x 1 high (landscape), has black


class TestPpmPerimeter:
    def test_return_type(self):
        assert isinstance(ppm_perimeter(_1X1_RED), int)

    def test_exact_4_for_1x1(self):
        # 1x1: perimeter = 2*(1+1) = 4
        assert ppm_perimeter(_1X1_RED) == 4

    def test_exact_8_for_2x2(self):
        # 2x2: perimeter = 2*(2+2) = 8
        assert ppm_perimeter(_2X2_RGBW) == 8

    def test_exact_8_for_3x1(self):
        # 3x1: perimeter = 2*(3+1) = 8
        assert ppm_perimeter(_3X1_GRAD) == 8

    def test_nonnegative(self):
        assert ppm_perimeter(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_perimeter(_1X1_RED) == ppm_perimeter(_1X1_RED)


class TestPpmDimensionRatio:
    def test_return_type(self):
        assert isinstance(ppm_dimension_ratio(_1X1_RED), float)

    def test_exact_1_0_for_1x1(self):
        # 1x1: ratio = 1/1 = 1.0
        assert ppm_dimension_ratio(_1X1_RED) == 1.0

    def test_exact_1_0_for_2x2(self):
        # 2x2: ratio = 2/2 = 1.0
        assert ppm_dimension_ratio(_2X2_RGBW) == 1.0

    def test_exact_3_0_for_3x1(self):
        # 3x1: ratio = 3/1 = 3.0 (width/height)
        assert ppm_dimension_ratio(_3X1_GRAD) == 3.0

    def test_nonnegative(self):
        assert ppm_dimension_ratio(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_dimension_ratio(_1X1_RED) == ppm_dimension_ratio(_1X1_RED)


class TestPpmIsSquare:
    def test_return_type(self):
        assert isinstance(ppm_is_square(_1X1_RED), bool)

    def test_true_for_1x1(self):
        assert ppm_is_square(_1X1_RED) is True

    def test_true_for_2x2(self):
        assert ppm_is_square(_2X2_RGBW) is True

    def test_false_for_3x1(self):
        # 3 wide x 1 high is not square
        assert ppm_is_square(_3X1_GRAD) is False

    def test_consistent_across_calls(self):
        assert ppm_is_square(_1X1_RED) == ppm_is_square(_1X1_RED)


class TestPpmIsLandscape:
    def test_return_type(self):
        assert isinstance(ppm_is_landscape(_1X1_RED), bool)

    def test_false_for_1x1(self):
        # Square is not landscape
        assert ppm_is_landscape(_1X1_RED) is False

    def test_false_for_2x2(self):
        # Square is not landscape
        assert ppm_is_landscape(_2X2_RGBW) is False

    def test_true_for_3x1(self):
        # 3 wide x 1 high is landscape
        assert ppm_is_landscape(_3X1_GRAD) is True

    def test_consistent_across_calls(self):
        assert ppm_is_landscape(_3X1_GRAD) == ppm_is_landscape(_3X1_GRAD)


class TestPpmMaxDimension:
    def test_return_type(self):
        assert isinstance(ppm_max_dimension(_1X1_RED), int)

    def test_exact_1_for_1x1(self):
        assert ppm_max_dimension(_1X1_RED) == 1

    def test_exact_2_for_2x2(self):
        assert ppm_max_dimension(_2X2_RGBW) == 2

    def test_exact_3_for_3x1(self):
        # max(3, 1) = 3
        assert ppm_max_dimension(_3X1_GRAD) == 3

    def test_nonnegative(self):
        assert ppm_max_dimension(_1X1_RED) >= 1

    def test_consistent_across_calls(self):
        assert ppm_max_dimension(_1X1_RED) == ppm_max_dimension(_1X1_RED)


class TestPpmHasPureBlack:
    def test_return_type(self):
        assert isinstance(ppm_has_pure_black(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        # 1x1-red.ppm: pure red (255,0,0), no black
        assert ppm_has_pure_black(_1X1_RED) is False

    def test_false_for_2x2_rgbw(self):
        # 2x2-rgbw: R,G,B,W pixels — no pure black (0,0,0)
        assert ppm_has_pure_black(_2X2_RGBW) is False

    def test_true_for_3x1_gradient(self):
        # 3x1-gradient: starts at (0,0,0) -> has pure black
        assert ppm_has_pure_black(_3X1_GRAD) is True

    def test_consistent_across_calls(self):
        assert ppm_has_pure_black(_1X1_RED) == ppm_has_pure_black(_1X1_RED)


class TestPpmMaxChannelSum:
    def test_return_type(self):
        assert isinstance(ppm_max_channel_sum(_1X1_RED), int)

    def test_exact_255_for_1x1_red(self):
        # max channel sum for 1x1-red: max(R+G+B for all pixels) = 255+0+0 = 255
        assert ppm_max_channel_sum(_1X1_RED) == 255

    def test_exact_765_for_2x2_rgbw(self):
        # 2x2 has white pixel (255,255,255): sum = 765
        assert ppm_max_channel_sum(_2X2_RGBW) == 765

    def test_exact_765_for_3x1_gradient(self):
        # 3x1 has white or bright pixel at end -> 765
        assert ppm_max_channel_sum(_3X1_GRAD) == 765

    def test_nonnegative(self):
        assert ppm_max_channel_sum(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_max_channel_sum(_1X1_RED) == ppm_max_channel_sum(_1X1_RED)
