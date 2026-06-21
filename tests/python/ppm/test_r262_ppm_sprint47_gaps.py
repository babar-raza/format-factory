"""Tests for PPM Sprint 47 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_COLD_PIX-001  (Ppm Cold Pixel Ratio)
  GAP-PPM-FOSS-PPM_RED_GREE-001  (Ppm Red Green Diff)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_cold_pixel_ratio, ppm_red_green_diff

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED_1X1 = str(_DIR / "1x1-red.ppm")
_RGBW_2X2 = str(_DIR / "2x2-rgbw.ppm")
_GRADIENT_3X1 = str(_DIR / "3x1-gradient.ppm")


class TestPpmColdPixelRatio:
    def test_return_type(self):
        assert isinstance(ppm_cold_pixel_ratio(_RED_1X1), (int, float))

    def test_zero_for_all_red_1x1(self):
        assert ppm_cold_pixel_ratio(_RED_1X1) == 0.0

    def test_exact_0_25_for_2x2_rgbw(self):
        assert ppm_cold_pixel_ratio(_RGBW_2X2) == 0.25

    def test_in_range_0_to_1(self):
        assert 0.0 <= ppm_cold_pixel_ratio(_RED_1X1) <= 1.0

    def test_consistent_across_calls(self):
        assert ppm_cold_pixel_ratio(_RED_1X1) == ppm_cold_pixel_ratio(_RED_1X1)


class TestPpmRedGreenDiff:
    def test_return_type(self):
        assert isinstance(ppm_red_green_diff(_RED_1X1), (int, float))

    def test_exact_255_for_1x1_red(self):
        assert ppm_red_green_diff(_RED_1X1) == 255.0

    def test_zero_for_2x2_rgbw(self):
        assert ppm_red_green_diff(_RGBW_2X2) == 0.0

    def test_nonnegative(self):
        assert ppm_red_green_diff(_RED_1X1) >= 0

    def test_consistent_across_calls(self):
        assert ppm_red_green_diff(_RED_1X1) == ppm_red_green_diff(_RED_1X1)
