"""
PPM FOSS gap closure tests.

Closes:
  GAP-PPM-FOSS-PPM_IS_MONOC-001  — ppm_is_monochrome
  GAP-PPM-FOSS-PPM_TOTAL_CH-001  — ppm_total_channel_sum
  GAP-PPM-FOSS-PPM_AVG_BRIG-001  — ppm_avg_brightness
  GAP-PPM-FOSS-PPM_COLOR_VA-001  — ppm_color_variance
  GAP-PPM-FOSS-PPM_RED_RATI-001  — ppm_red_ratio
  GAP-PPM-FOSS-PPM_BORDER_B-001  — ppm_border_brightness
  GAP-PPM-FOSS-PPM_GREEN_RA-001  — ppm_green_ratio
  GAP-PPM-FOSS-PPM_PIXEL_BR-001  — ppm_pixel_brightness_range
  GAP-PPM-FOSS-PPM_BLUE_RAT-001  — ppm_blue_ratio
  GAP-PPM-FOSS-PPM_IS_BRIGH-001  — ppm_is_bright
  GAP-PPM-FOSS-PPM_MAXVAL-001    — ppm_maxval
  GAP-PPM-FOSS-PPM_NORMALIZ-001  — ppm_normalized_brightness
  GAP-PPM-FOSS-PPM_AREA-001      — ppm_area
  GAP-PPM-FOSS-PPM_MAX_PIXE-001  — ppm_max_pixel_brightness

Run from repo root:
    python -m pytest tests/python/ppm/test_ppm_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from ppm.ppm_parser import (
    ppm_is_monochrome,
    ppm_total_channel_sum,
    ppm_avg_brightness,
    ppm_color_variance,
    ppm_red_ratio,
    ppm_border_brightness,
    ppm_green_ratio,
    ppm_pixel_brightness_range,
    ppm_blue_ratio,
    ppm_is_bright,
    ppm_maxval,
    ppm_normalized_brightness,
    ppm_area,
    ppm_max_pixel_brightness,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "ppm" / "valid"
RED = SAMPLES / "1x1-red.ppm"
RGBW = SAMPLES / "2x2-rgbw.ppm"
GRADIENT = SAMPLES / "3x1-gradient.ppm"


class TestPpmIsMonochrome:
    def test_red_is_monochrome(self):
        assert ppm_is_monochrome(RED) is True

    def test_returns_bool(self):
        assert isinstance(ppm_is_monochrome(RED), bool)


class TestPpmTotalChannelSum:
    def test_red_is_255(self):
        assert ppm_total_channel_sum(RED) == 255

    def test_returns_int(self):
        assert isinstance(ppm_total_channel_sum(RED), int)

    def test_positive(self):
        for p in [RED, RGBW]:
            assert ppm_total_channel_sum(p) > 0


class TestPpmAvgBrightness:
    def test_red_value(self):
        assert ppm_avg_brightness(RED) == pytest.approx(85.0, abs=0.1)

    def test_returns_numeric(self):
        assert isinstance(ppm_avg_brightness(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_avg_brightness(p) >= 0


class TestPpmColorVariance:
    def test_red_zero_variance(self):
        assert ppm_color_variance(RED) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(ppm_color_variance(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_color_variance(p) >= 0


class TestPpmRedRatio:
    def test_red_is_one(self):
        assert ppm_red_ratio(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(ppm_red_ratio(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, RGBW, GRADIENT]:
            r = ppm_red_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPpmBorderBrightness:
    def test_returns_numeric(self):
        assert isinstance(ppm_border_brightness(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_border_brightness(p) >= 0


class TestPpmGreenRatio:
    def test_red_is_zero(self):
        assert ppm_green_ratio(RED) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(ppm_green_ratio(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, RGBW, GRADIENT]:
            r = ppm_green_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPpmPixelBrightnessRange:
    def test_red_zero_range(self):
        assert ppm_pixel_brightness_range(RED) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(ppm_pixel_brightness_range(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_pixel_brightness_range(p) >= 0


class TestPpmBlueRatio:
    def test_red_is_zero(self):
        assert ppm_blue_ratio(RED) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(ppm_blue_ratio(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, RGBW, GRADIENT]:
            r = ppm_blue_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPpmIsBright:
    def test_returns_bool(self):
        assert isinstance(ppm_is_bright(RED), bool)


class TestPpmMaxval:
    def test_red_is_255(self):
        assert ppm_maxval(RED) == 255

    def test_returns_int(self):
        assert isinstance(ppm_maxval(RED), int)

    def test_positive(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_maxval(p) > 0


class TestPpmNormalizedBrightness:
    def test_returns_numeric(self):
        assert isinstance(ppm_normalized_brightness(RED), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [RED, RGBW, GRADIENT]:
            r = ppm_normalized_brightness(p)
            assert 0.0 <= r <= 1.0


class TestPpmArea:
    def test_red_is_one(self):
        assert ppm_area(RED) == 1

    def test_rgbw_is_four(self):
        assert ppm_area(RGBW) == 4

    def test_returns_int(self):
        assert isinstance(ppm_area(RED), int)

    def test_positive(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_area(p) > 0


class TestPpmMaxPixelBrightness:
    def test_returns_numeric(self):
        assert isinstance(ppm_max_pixel_brightness(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, RGBW, GRADIENT]:
            assert ppm_max_pixel_brightness(p) >= 0
