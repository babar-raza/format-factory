"""Tests for ppm_has_pure_black and ppm_max_channel_sum (Sprint 43)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_has_pure_black, ppm_max_channel_sum

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")       # (255,0,0): no pure black, max_sum=255
_RGBW = str(_DIR / "2x2-rgbw.ppm")    # R,G,B,W: no pure black, max_sum=765
_GRAD = str(_DIR / "3x1-gradient.ppm") # (0,0,0),(128,128,128),(255,255,255): has black, max_sum=765


class TestPpmHasPureBlack:
    def test_return_type(self):
        assert isinstance(ppm_has_pure_black(_RED), bool)

    def test_false_for_red(self):
        # 1x1-red: single (255,0,0) pixel, no pure black
        assert ppm_has_pure_black(_RED) is False

    def test_false_for_rgbw(self):
        # 2x2-rgbw: R, G, B, W — none are pure black
        assert ppm_has_pure_black(_RGBW) is False

    def test_true_for_gradient(self):
        # 3x1-gradient: first pixel is (0,0,0) — pure black
        assert ppm_has_pure_black(_GRAD) is True

    def test_consistent_across_calls(self):
        assert ppm_has_pure_black(_GRAD) == ppm_has_pure_black(_GRAD)

    def test_false_is_not_none(self):
        result = ppm_has_pure_black(_RED)
        assert result is False
        assert result is not None


class TestPpmMaxChannelSum:
    def test_return_type(self):
        assert isinstance(ppm_max_channel_sum(_RED), int)

    def test_exact_255_for_red(self):
        # 1x1-red: (255,0,0) -> sum=255
        assert ppm_max_channel_sum(_RED) == 255

    def test_exact_765_for_rgbw(self):
        # 2x2-rgbw: white pixel (255,255,255) -> max sum=765
        assert ppm_max_channel_sum(_RGBW) == 765

    def test_exact_765_for_gradient(self):
        # 3x1-gradient: (255,255,255) -> max sum=765
        assert ppm_max_channel_sum(_GRAD) == 765

    def test_nonnegative(self):
        assert ppm_max_channel_sum(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_max_channel_sum(_RGBW) == ppm_max_channel_sum(_RGBW)

    def test_at_most_max_possible(self):
        # Max possible is 3 * 255 = 765
        assert ppm_max_channel_sum(_RGBW) <= 765
