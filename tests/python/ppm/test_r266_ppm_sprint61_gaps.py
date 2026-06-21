"""Tests for PPM Sprint 61 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_HUE_DIVE-001   (Ppm Hue Diversity)
  GAP-PPM-FOSS-PPM_CENTER_B-001   (Ppm Center Brightness)
  GAP-PPM-FOSS-PPM_MAX_GREE-001   (Ppm Max Green Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_hue_diversity, ppm_center_brightness, ppm_max_green_value

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2 = str(_DIR / "2x2-rgbw.ppm")
_3X1 = str(_DIR / "3x1-gradient.ppm")


class TestPpmHueDiversity:
    def test_return_type(self):
        assert isinstance(ppm_hue_diversity(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_hue_diversity(_1X1_RED) == 1

    def test_exact_3_for_2x2(self):
        assert ppm_hue_diversity(_2X2) == 3

    def test_exact_0_for_gradient(self):
        assert ppm_hue_diversity(_3X1) == 0

    def test_nonnegative(self):
        assert ppm_hue_diversity(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_hue_diversity(_1X1_RED) == ppm_hue_diversity(_1X1_RED)


class TestPpmCenterBrightness:
    def test_return_type(self):
        assert isinstance(ppm_center_brightness(_1X1_RED), (int, float))

    def test_zero_for_1x1(self):
        assert ppm_center_brightness(_1X1_RED) == 0.0

    def test_exact_85_for_2x2(self):
        assert ppm_center_brightness(_2X2) == 85.0

    def test_zero_for_gradient(self):
        assert ppm_center_brightness(_3X1) == 0.0

    def test_nonnegative(self):
        assert ppm_center_brightness(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_center_brightness(_1X1_RED) == ppm_center_brightness(_1X1_RED)


class TestPpmMaxGreenValue:
    def test_return_type(self):
        assert isinstance(ppm_max_green_value(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        assert ppm_max_green_value(_1X1_RED) == 0

    def test_exact_255_for_2x2(self):
        assert ppm_max_green_value(_2X2) == 255

    def test_exact_255_for_gradient(self):
        assert ppm_max_green_value(_3X1) == 255

    def test_between_0_and_255(self):
        assert 0 <= ppm_max_green_value(_1X1_RED) <= 255

    def test_consistent_across_calls(self):
        assert ppm_max_green_value(_1X1_RED) == ppm_max_green_value(_1X1_RED)
