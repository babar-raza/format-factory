"""Tests for PPM Sprint 41 batch 3 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_MIN_CHAN-001  (Ppm Min Channel Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_min_channel_value

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRADIENT = str(_DIR / "3x1-gradient.ppm")


class TestPpmMinChannelValue:
    def test_return_type(self):
        assert isinstance(ppm_min_channel_value(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        assert ppm_min_channel_value(_1X1_RED) == 0

    def test_zero_for_2x2_rgbw(self):
        assert ppm_min_channel_value(_2X2_RGBW) == 0

    def test_zero_for_3x1_gradient(self):
        assert ppm_min_channel_value(_3X1_GRADIENT) == 0

    def test_nonnegative(self):
        assert ppm_min_channel_value(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_min_channel_value(_1X1_RED) == ppm_min_channel_value(_1X1_RED)
