"""Tests for PPM Sprint 68 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_RED_MEAN-001   (Ppm Red Mean Value)
  GAP-PPM-FOSS-PPM_PIXEL_CO-001   (Ppm Pixel Count Total)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_red_mean_value, ppm_pixel_count_total

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")
_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmRedMeanValue:
    def test_return_type(self):
        assert isinstance(ppm_red_mean_value(_RED), (int, float))

    def test_exact_255_for_1x1_red(self):
        assert ppm_red_mean_value(_RED) == 255.0

    def test_exact_127_5_for_rgbw(self):
        assert ppm_red_mean_value(_RGBW) == pytest.approx(127.5)

    def test_approx_127_67_for_gradient(self):
        assert ppm_red_mean_value(_GRAD) == pytest.approx(127.667, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_red_mean_value(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_red_mean_value(_RED) == ppm_red_mean_value(_RED)


class TestPpmPixelCountTotal:
    def test_return_type(self):
        assert isinstance(ppm_pixel_count_total(_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_pixel_count_total(_RED) == 1

    def test_exact_4_for_rgbw(self):
        assert ppm_pixel_count_total(_RGBW) == 4

    def test_exact_3_for_gradient(self):
        assert ppm_pixel_count_total(_GRAD) == 3

    def test_positive(self):
        assert ppm_pixel_count_total(_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_pixel_count_total(_RED) == ppm_pixel_count_total(_RED)
