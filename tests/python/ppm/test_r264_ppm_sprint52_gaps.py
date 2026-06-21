"""Tests for PPM Sprint 52 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_TOTAL_BL-001  (Ppm Total Blue Sum)
  GAP-PPM-FOSS-PPM_MAX_RED_-001  (Ppm Max Red Value)
  GAP-PPM-FOSS-PPM_MIN_BRIG-001  (Ppm Min Brightness)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_total_blue_sum, ppm_max_red_value, ppm_min_brightness

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")


class TestPpmTotalBlueSum:
    def test_return_type(self):
        assert isinstance(ppm_total_blue_sum(_RED), (int, float))

    def test_zero_for_red(self):
        assert ppm_total_blue_sum(_RED) == 0

    def test_exact_510_for_rgbw(self):
        assert ppm_total_blue_sum(_RGBW) == 510

    def test_nonnegative(self):
        assert ppm_total_blue_sum(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_total_blue_sum(_RED) == ppm_total_blue_sum(_RED)


class TestPpmMaxRedValue:
    def test_return_type(self):
        assert isinstance(ppm_max_red_value(_RED), (int, float))

    def test_exact_255_for_red(self):
        assert ppm_max_red_value(_RED) == 255

    def test_exact_255_for_rgbw(self):
        assert ppm_max_red_value(_RGBW) == 255

    def test_nonnegative(self):
        assert ppm_max_red_value(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_max_red_value(_RED) == ppm_max_red_value(_RED)


class TestPpmMinBrightness:
    def test_return_type(self):
        assert isinstance(ppm_min_brightness(_RED), (int, float))

    def test_exact_85_for_red(self):
        assert ppm_min_brightness(_RED) == 85.0

    def test_exact_85_for_rgbw(self):
        assert ppm_min_brightness(_RGBW) == 85.0

    def test_nonnegative(self):
        assert ppm_min_brightness(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_min_brightness(_RED) == ppm_min_brightness(_RED)
