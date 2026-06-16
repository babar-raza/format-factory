"""Tests for ppm_min_channel_sum (Sprint 39).

Closes:
  GAP-PPM-FOSS-PPM_MIN_CHAN-001  (Ppm Min Channel Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_min_channel_sum

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")           # red: (255,0,0)
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")         # RGBW corners
_3X1_GRAD = str(_DIR / "3x1-gradient.ppm")     # gradient starts at black


class TestPpmMinChannelSum:
    def test_return_type(self):
        assert isinstance(ppm_min_channel_sum(_1X1_RED), int)

    def test_exact_255_for_1x1_red(self):
        # 1x1-red: single red pixel (255,0,0) -> min channel sum = 255
        assert ppm_min_channel_sum(_1X1_RED) == 255

    def test_exact_255_for_2x2_rgbw(self):
        # 2x2 RGBW: min per-pixel sum (red=255, green=255, blue=255, white=765) -> min=255
        assert ppm_min_channel_sum(_2X2_RGBW) == 255

    def test_zero_for_3x1_gradient(self):
        # 3x1 gradient starts at black (0,0,0) -> min channel sum = 0
        assert ppm_min_channel_sum(_3X1_GRAD) == 0

    def test_nonnegative(self):
        assert ppm_min_channel_sum(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_min_channel_sum(_1X1_RED) == ppm_min_channel_sum(_1X1_RED)
