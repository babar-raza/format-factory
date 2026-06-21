"""Tests for PPM gap closure batch 2 (Sprint 40).

Closes:
  GAP-PPM-FOSS-PPM_MIN_CHAN-001   (Ppm Min Channel Avg)
  GAP-PPM-FOSS-PPM_MAX_PIXE-001  (Ppm Max Pixel Brightness)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_max_pixel_brightness, ppm_min_channel_avg

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmMinChannelAvg:
    def test_return_type(self):
        assert isinstance(ppm_min_channel_avg(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # (255, 0, 0) -> min channel avg = 0.0 (green/blue are 0)
        assert ppm_min_channel_avg(_1X1_RED) == 0.0

    def test_nonnegative(self):
        assert ppm_min_channel_avg(_1X1_RED) >= 0.0

    def test_positive_for_2x2_rgbw(self):
        # RGBW has white pixel so min channel avg > 0
        assert ppm_min_channel_avg(_2X2_RGBW) > 0

    def test_consistent_across_calls(self):
        assert ppm_min_channel_avg(_1X1_RED) == ppm_min_channel_avg(_1X1_RED)


class TestPpmMaxPixelBrightness:
    def test_return_type(self):
        assert isinstance(ppm_max_pixel_brightness(_1X1_RED), float)

    def test_exact_85_for_1x1_red(self):
        # red pixel (255,0,0): brightness = (255+0+0)/3 = 85.0
        assert ppm_max_pixel_brightness(_1X1_RED) == 85.0

    def test_exact_255_for_2x2_rgbw(self):
        # white pixel (255,255,255): brightness = 255.0
        assert ppm_max_pixel_brightness(_2X2_RGBW) == 255.0

    def test_positive(self):
        assert ppm_max_pixel_brightness(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_max_pixel_brightness(_1X1_RED) == ppm_max_pixel_brightness(_1X1_RED)
