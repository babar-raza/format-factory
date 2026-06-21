"""Tests for PPM gap closure batch 3 (Sprint 40).

Closes:
  GAP-PPM-FOSS-PPM_LUMINANC-001   (Ppm Luminance Sum)
  GAP-PPM-FOSS-PPM_DARK_PIX-001   (Ppm Dark Pixel Ratio)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_dark_pixel_ratio, ppm_luminance_sum

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmLuminanceSum:
    def test_return_type(self):
        assert isinstance(ppm_luminance_sum(_1X1_RED), float)

    def test_positive_for_1x1_red(self):
        # red pixel has nonzero luminance
        assert ppm_luminance_sum(_1X1_RED) > 0

    def test_exact_approx_54_for_1x1_red(self):
        # R=255, G=0, B=0 -> luminance = 0.2126*255 ≈ 54.213
        assert abs(ppm_luminance_sum(_1X1_RED) - 54.213) < 0.01

    def test_larger_for_multi_pixel(self):
        # more pixels with varying brightness = higher sum
        assert ppm_luminance_sum(_2X2_RGBW) > ppm_luminance_sum(_1X1_RED)

    def test_nonnegative(self):
        assert ppm_luminance_sum(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_luminance_sum(_1X1_RED) == ppm_luminance_sum(_1X1_RED)


class TestPpmDarkPixelRatio:
    def test_return_type(self):
        assert isinstance(ppm_dark_pixel_ratio(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        # red (brightness=85) is below dark threshold -> ratio 1.0
        assert ppm_dark_pixel_ratio(_1X1_RED) == 1.0

    def test_between_0_and_1(self):
        r = ppm_dark_pixel_ratio(_2X2_RGBW)
        assert 0.0 <= r <= 1.0

    def test_positive_for_2x2_rgbw(self):
        # 3 of 4 pixels are dark (R, G, B) -> 0.75
        assert ppm_dark_pixel_ratio(_2X2_RGBW) == 0.75

    def test_nonnegative(self):
        assert ppm_dark_pixel_ratio(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_dark_pixel_ratio(_1X1_RED) == ppm_dark_pixel_ratio(_1X1_RED)
