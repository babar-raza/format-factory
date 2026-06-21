"""
QOI FOSS gap closure tests.

Closes:
  GAP-QOI-FOSS-QOI_IS_DARK-001        — qoi_is_dark
  GAP-QOI-FOSS-QOI_COLOR_DE-001       — qoi_color_depth_estimate
  GAP-QOI-FOSS-QOI_IS_BRIGH-001       — qoi_is_bright
  GAP-QOI-FOSS-QOI_SATURATI-001       — qoi_saturation_estimate
  GAP-QOI-FOSS-QOI_PIXEL_CO-001       — qoi_pixel_contrast
  GAP-QOI-FOSS-QOI_TOTAL_RG-001       — qoi_total_rgb_sum
  GAP-QOI-FOSS-QOI_RED_BLUE-001       — qoi_red_blue_ratio
  GAP-QOI-FOSS-QOI_NORMALIZ-001       — qoi_normalized_brightness
  GAP-QOI-FOSS-QOI_MIN_BRIG-001       — qoi_min_brightness
  GAP-QOI-FOSS-QOI_ABOVE_ME-001       — qoi_above_mean_ratio
  GAP-QOI-FOSS-QOI_IS_WIDE-001        — qoi_is_wide

Run from repo root:
    python -m pytest tests/python/qoi/test_qoi_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from qoi.qoi_parser import (
    qoi_is_dark,
    qoi_color_depth_estimate,
    qoi_is_bright,
    qoi_saturation_estimate,
    qoi_pixel_contrast,
    qoi_total_rgb_sum,
    qoi_red_blue_ratio,
    qoi_normalized_brightness,
    qoi_min_brightness,
    qoi_above_mean_ratio,
    qoi_is_wide,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "qoi" / "valid"
RED = SAMPLES / "1x1-red.qoi"
BLACK = SAMPLES / "2x2-black.qoi"
GRADIENT = SAMPLES / "4x1-gradient.qoi"


class TestQoiIsDark:
    def test_black_is_dark(self):
        assert qoi_is_dark(BLACK) is True

    def test_red_is_dark(self):
        # single red pixel with low overall brightness
        assert qoi_is_dark(RED) is True

    def test_returns_bool(self):
        assert isinstance(qoi_is_dark(BLACK), bool)


class TestQoiColorDepthEstimate:
    def test_returns_numeric(self):
        assert isinstance(qoi_color_depth_estimate(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, BLACK, GRADIENT]:
            assert qoi_color_depth_estimate(p) >= 0


class TestQoiIsBright:
    def test_black_not_bright(self):
        assert qoi_is_bright(BLACK) is False

    def test_returns_bool(self):
        assert isinstance(qoi_is_bright(RED), bool)


class TestQoiSaturationEstimate:
    def test_black_zero_saturation(self):
        assert qoi_saturation_estimate(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_red_has_saturation(self):
        assert qoi_saturation_estimate(RED) > 0

    def test_returns_numeric(self):
        assert isinstance(qoi_saturation_estimate(RED), (int, float))

    def test_bounded(self):
        for p in [RED, BLACK, GRADIENT]:
            r = qoi_saturation_estimate(p)
            assert r >= 0


class TestQoiPixelContrast:
    def test_black_zero_contrast(self):
        assert qoi_pixel_contrast(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(qoi_pixel_contrast(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, BLACK, GRADIENT]:
            assert qoi_pixel_contrast(p) >= 0


class TestQoiTotalRgbSum:
    def test_black_zero(self):
        assert qoi_total_rgb_sum(BLACK) == 0

    def test_red_positive(self):
        assert qoi_total_rgb_sum(RED) > 0

    def test_returns_int_or_numeric(self):
        assert isinstance(qoi_total_rgb_sum(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, BLACK, GRADIENT]:
            assert qoi_total_rgb_sum(p) >= 0


class TestQoiRedBlueRatio:
    def test_black_zero(self):
        assert qoi_red_blue_ratio(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(qoi_red_blue_ratio(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, BLACK, GRADIENT]:
            assert qoi_red_blue_ratio(p) >= 0


class TestQoiNormalizedBrightness:
    def test_black_zero(self):
        assert qoi_normalized_brightness(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(qoi_normalized_brightness(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, BLACK, GRADIENT]:
            r = qoi_normalized_brightness(p)
            assert 0.0 <= r <= 1.0


class TestQoiMinBrightness:
    def test_black_zero(self):
        assert qoi_min_brightness(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(qoi_min_brightness(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, BLACK, GRADIENT]:
            assert qoi_min_brightness(p) >= 0


class TestQoiAboveMeanRatio:
    def test_black_zero(self):
        assert qoi_above_mean_ratio(BLACK) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(qoi_above_mean_ratio(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, BLACK, GRADIENT]:
            r = qoi_above_mean_ratio(p)
            assert 0.0 <= r <= 1.0


class TestQoiIsWide:
    def test_1x1_not_wide(self):
        assert qoi_is_wide(RED) is False

    def test_4x1_is_wide(self):
        assert qoi_is_wide(GRADIENT) is True

    def test_returns_bool(self):
        assert isinstance(qoi_is_wide(RED), bool)
