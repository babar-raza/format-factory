"""Tests for qoi geometry and color analytics (Sprint 39).

Closes:
  GAP-QOI-FOSS-QOI_BLUE_DOM-001  (Qoi Blue Dominant)
  GAP-QOI-FOSS-QOI_GREEN_DO-001  (Qoi Green Dominant)
  GAP-QOI-FOSS-QOI_IS_SQUAR-001  (Qoi Is Square)
  GAP-QOI-FOSS-QOI_PERIMETE-001  (Qoi Perimeter)
  GAP-QOI-FOSS-QOI_COLOR_VA-001  (Qoi Color Variance)
  GAP-QOI-FOSS-QOI_DIMENSIO-001  (Qoi Dimension Ratio)
  GAP-QOI-FOSS-QOI_IS_LANDS-001  (Qoi Is Landscape)
  GAP-QOI-FOSS-QOI_IS_PORTR-001  (Qoi Is Portrait)
  GAP-QOI-FOSS-QOI_MAX_DIME-001  (Qoi Max Dimension)
  GAP-QOI-FOSS-QOI_HAS_ANY_-001  (Qoi Has Any Black)
  GAP-QOI-FOSS-QOI_MAX_CHAN-001  (Qoi Max Channel Average)
  GAP-QOI-FOSS-QOI_MIN_CHAN-001  (Qoi Min Channel Average)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_blue_dominant,
    qoi_color_variance,
    qoi_dimension_ratio,
    qoi_green_dominant,
    qoi_has_any_black,
    qoi_is_landscape,
    qoi_is_portrait,
    qoi_is_square,
    qoi_max_channel_average,
    qoi_max_dimension,
    qoi_min_channel_average,
    qoi_perimeter,
)

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")           # 1x1 square, red
_2X2_BLACK = str(_DIR / "2x2-black.qoi")        # 2x2 square, all black
_4X1_GRAD = str(_DIR / "4x1-gradient.qoi")      # 4 wide x 1 high (landscape)


class TestQoiIsSquare:
    def test_true_for_1x1(self):
        assert qoi_is_square(_1X1_RED) is True

    def test_true_for_2x2(self):
        assert qoi_is_square(_2X2_BLACK) is True

    def test_false_for_4x1(self):
        assert qoi_is_square(_4X1_GRAD) is False

    def test_return_type(self):
        assert isinstance(qoi_is_square(_1X1_RED), bool)


class TestQoiPerimeter:
    def test_exact_4_for_1x1(self):
        assert qoi_perimeter(_1X1_RED) == 4

    def test_exact_8_for_2x2(self):
        assert qoi_perimeter(_2X2_BLACK) == 8

    def test_exact_10_for_4x1(self):
        # 2*(4+1) = 10
        assert qoi_perimeter(_4X1_GRAD) == 10

    def test_return_type(self):
        assert isinstance(qoi_perimeter(_1X1_RED), int)


class TestQoiDimensionRatio:
    def test_exact_1_0_for_1x1(self):
        assert qoi_dimension_ratio(_1X1_RED) == 1.0

    def test_exact_1_0_for_2x2(self):
        assert qoi_dimension_ratio(_2X2_BLACK) == 1.0

    def test_exact_4_0_for_4x1(self):
        # 4/1 = 4.0
        assert qoi_dimension_ratio(_4X1_GRAD) == 4.0

    def test_return_type(self):
        assert isinstance(qoi_dimension_ratio(_1X1_RED), float)


class TestQoiIsLandscape:
    def test_false_for_1x1_square(self):
        assert qoi_is_landscape(_1X1_RED) is False

    def test_false_for_2x2_square(self):
        assert qoi_is_landscape(_2X2_BLACK) is False

    def test_true_for_4x1(self):
        assert qoi_is_landscape(_4X1_GRAD) is True


class TestQoiIsPortrait:
    def test_false_for_1x1_square(self):
        # Square (1x1) is not portrait (height > width)
        assert qoi_is_portrait(_1X1_RED) is False

    def test_false_for_4x1_landscape(self):
        assert qoi_is_portrait(_4X1_GRAD) is False


class TestQoiMaxDimension:
    def test_exact_1_for_1x1(self):
        assert qoi_max_dimension(_1X1_RED) == 1

    def test_exact_2_for_2x2(self):
        assert qoi_max_dimension(_2X2_BLACK) == 2

    def test_exact_4_for_4x1(self):
        assert qoi_max_dimension(_4X1_GRAD) == 4

    def test_return_type(self):
        assert isinstance(qoi_max_dimension(_1X1_RED), int)


class TestQoiHasAnyBlack:
    def test_false_for_1x1_red(self):
        # red pixel has no black
        assert qoi_has_any_black(_1X1_RED) is False

    def test_true_for_2x2_black(self):
        # all black pixels
        assert qoi_has_any_black(_2X2_BLACK) is True

    def test_true_for_4x1_gradient(self):
        # gradient starts at black
        assert qoi_has_any_black(_4X1_GRAD) is True

    def test_return_type(self):
        assert isinstance(qoi_has_any_black(_1X1_RED), bool)


class TestQoiMaxChannelAverage:
    def test_exact_255_for_1x1_red(self):
        # red: R=255, G=0, B=0 -> max channel avg = 255.0
        assert qoi_max_channel_average(_1X1_RED) == 255.0

    def test_zero_for_2x2_black(self):
        # all black: R=G=B=0 -> max channel avg = 0.0
        assert qoi_max_channel_average(_2X2_BLACK) == 0.0

    def test_return_type(self):
        assert isinstance(qoi_max_channel_average(_1X1_RED), float)


class TestQoiMinChannelAverage:
    def test_exact_0_for_1x1_red(self):
        # red: G=0, B=0 -> min channel avg = 0.0
        assert qoi_min_channel_average(_1X1_RED) == 0.0

    def test_zero_for_2x2_black(self):
        # all black: all channels 0 -> min = 0.0
        assert qoi_min_channel_average(_2X2_BLACK) == 0.0

    def test_return_type(self):
        assert isinstance(qoi_min_channel_average(_1X1_RED), float)


class TestQoiColorVariance:
    def test_nonzero_for_1x1_red(self):
        # red pixel has variance across channels
        assert qoi_color_variance(_1X1_RED) > 0.0

    def test_exact_14450_for_1x1_red(self):
        # Based on probe: 14450.0
        assert qoi_color_variance(_1X1_RED) == 14450.0

    def test_zero_for_2x2_black(self):
        # All pixels identical (0,0,0) -> variance = 0.0
        assert qoi_color_variance(_2X2_BLACK) == 0.0

    def test_return_type(self):
        assert isinstance(qoi_color_variance(_1X1_RED), float)


class TestQoiBlueDominant:
    def test_false_for_1x1_red(self):
        # Red pixel: B not dominant
        assert qoi_blue_dominant(_1X1_RED) is False

    def test_false_for_2x2_black(self):
        # Black: no channel dominant
        assert qoi_blue_dominant(_2X2_BLACK) is False

    def test_return_type(self):
        assert isinstance(qoi_blue_dominant(_1X1_RED), bool)


class TestQoiGreenDominant:
    def test_false_for_1x1_red(self):
        # Red pixel: G not dominant
        assert qoi_green_dominant(_1X1_RED) is False

    def test_false_for_2x2_black(self):
        assert qoi_green_dominant(_2X2_BLACK) is False

    def test_return_type(self):
        assert isinstance(qoi_green_dominant(_1X1_RED), bool)
