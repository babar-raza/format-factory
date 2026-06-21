"""Tests for PPM Sprint 41 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_WARM_PIX-001  (Ppm Warm Pixel Count)
  GAP-PPM-FOSS-PPM_COOL_PIX-001  (Ppm Cool Pixel Count)
  GAP-PPM-FOSS-PPM_GRAYSCAL-001  (Ppm Grayscale Pixel Count)
  GAP-PPM-FOSS-PPM_NEUTRAL_-001  (Ppm Neutral Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_cool_pixel_count,
    ppm_grayscale_pixel_count,
    ppm_neutral_pixel_count,
    ppm_warm_pixel_count,
)

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRADIENT = str(_DIR / "3x1-gradient.ppm")


class TestPpmWarmPixelCount:
    def test_return_type(self):
        assert isinstance(ppm_warm_pixel_count(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_warm_pixel_count(_1X1_RED) == 1

    def test_exact_1_for_2x2_rgbw(self):
        assert ppm_warm_pixel_count(_2X2_RGBW) == 1

    def test_nonnegative(self):
        assert ppm_warm_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_warm_pixel_count(_1X1_RED) == ppm_warm_pixel_count(_1X1_RED)


class TestPpmCoolPixelCount:
    def test_return_type(self):
        assert isinstance(ppm_cool_pixel_count(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        assert ppm_cool_pixel_count(_1X1_RED) == 0

    def test_exact_1_for_2x2_rgbw(self):
        assert ppm_cool_pixel_count(_2X2_RGBW) == 1

    def test_nonnegative(self):
        assert ppm_cool_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_cool_pixel_count(_1X1_RED) == ppm_cool_pixel_count(_1X1_RED)


class TestPpmGrayscalePixelCount:
    def test_return_type(self):
        assert isinstance(ppm_grayscale_pixel_count(_3X1_GRADIENT), int)

    def test_exact_3_for_3x1_gradient(self):
        assert ppm_grayscale_pixel_count(_3X1_GRADIENT) == 3

    def test_nonnegative(self):
        assert ppm_grayscale_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_grayscale_pixel_count(_3X1_GRADIENT) == ppm_grayscale_pixel_count(_3X1_GRADIENT)


class TestPpmNeutralPixelCount:
    def test_return_type(self):
        assert isinstance(ppm_neutral_pixel_count(_3X1_GRADIENT), int)

    def test_exact_3_for_3x1_gradient(self):
        assert ppm_neutral_pixel_count(_3X1_GRADIENT) == 3

    def test_nonnegative(self):
        assert ppm_neutral_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_neutral_pixel_count(_3X1_GRADIENT) == ppm_neutral_pixel_count(_3X1_GRADIENT)
