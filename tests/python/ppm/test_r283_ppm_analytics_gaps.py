"""
Tests for PPM analytics gap closure (4 FOSS gaps).
Closes: GAP-PPM-FOSS-PPM_IS_MONO-001, GAP-PPM-FOSS-PPM_TOTAL_C-001,
        GAP-PPM-FOSS-PPM_AVG_BR-001, GAP-PPM-FOSS-PPM_COLOR_V-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_is_monochrome,
    ppm_total_channel_sum,
    ppm_avg_brightness,
    ppm_color_variance,
)

_PPM_1x1 = _REPO / "samples/by-format/ppm/valid/1x1-red.ppm"
_PPM_2x2 = _REPO / "samples/by-format/ppm/valid/2x2-rgbw.ppm"
_PPM_GRAD = _REPO / "samples/by-format/ppm/valid/3x1-gradient.ppm"


class TestPpmIsMonochrome:
    def test_returns_bool(self):
        assert isinstance(ppm_is_monochrome(_PPM_1x1), bool)

    def test_single_color_pixel_is_monochrome(self):
        # 1x1-red.ppm has a single pixel; trivially monochrome
        assert ppm_is_monochrome(_PPM_1x1) is True

    def test_multicolor_image_not_monochrome(self):
        # 2x2-rgbw.ppm has red, green, blue, white pixels
        assert ppm_is_monochrome(_PPM_2x2) is False

    def test_gradient_not_monochrome(self):
        assert ppm_is_monochrome(_PPM_GRAD) is False


class TestPpmTotalChannelSum:
    def test_returns_int(self):
        assert isinstance(ppm_total_channel_sum(_PPM_1x1), int)

    def test_nonnegative(self):
        assert ppm_total_channel_sum(_PPM_1x1) >= 0

    def test_larger_for_more_pixels(self):
        # 2x2 has 4 pixels; 1x1 has 1; sum is larger
        assert ppm_total_channel_sum(_PPM_2x2) >= ppm_total_channel_sum(_PPM_1x1)

    def test_positive_for_colored_image(self):
        assert ppm_total_channel_sum(_PPM_1x1) > 0


class TestPpmAvgBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_avg_brightness(_PPM_1x1), float)

    def test_nonnegative(self):
        assert ppm_avg_brightness(_PPM_1x1) >= 0.0

    def test_at_most_255(self):
        assert ppm_avg_brightness(_PPM_1x1) <= 255.0

    def test_positive_for_colored_image(self):
        assert ppm_avg_brightness(_PPM_2x2) > 0.0


class TestPpmColorVariance:
    def test_returns_float(self):
        assert isinstance(ppm_color_variance(_PPM_2x2), float)

    def test_nonnegative(self):
        assert ppm_color_variance(_PPM_2x2) >= 0.0

    def test_zero_for_single_pixel(self):
        # Single pixel has no variance
        assert ppm_color_variance(_PPM_1x1) == 0.0

    def test_positive_for_varying_pixels(self):
        # 2x2-rgbw.ppm has 4 distinct color pixels
        assert ppm_color_variance(_PPM_2x2) > 0.0
