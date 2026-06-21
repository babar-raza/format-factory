"""Tests for PPM Sprint 74 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_NON_BLAC-001   (Ppm Non Black Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_non_black_pixel_count

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")
_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmNonBlackPixelCount:
    def test_return_type(self):
        assert isinstance(ppm_non_black_pixel_count(_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_non_black_pixel_count(_RED) == 1

    def test_exact_4_for_rgbw(self):
        assert ppm_non_black_pixel_count(_RGBW) == 4

    def test_exact_2_for_gradient(self):
        assert ppm_non_black_pixel_count(_GRAD) == 2

    def test_nonnegative(self):
        assert ppm_non_black_pixel_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_non_black_pixel_count(_RED) == ppm_non_black_pixel_count(_RED)
