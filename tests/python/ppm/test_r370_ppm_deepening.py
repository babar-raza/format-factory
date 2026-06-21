"""Tests for PPM product deepening sprint 141.

New functions:
  ppm_color_temperature_estimate  — (red_mean - blue_mean) / 255, range [-1, 1]
  ppm_channel_mean_std            — std of [red_mean, green_mean, blue_mean]
"""
import sys
import math
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_color_temperature_estimate, ppm_channel_mean_std

_RED = str(_REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm")
_RGBW = str(_REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm")
_GRAD = str(_REPO / "samples" / "by-format" / "ppm" / "valid" / "3x1-gradient.ppm")


class TestPpmColorTemperatureEstimate:
    def test_return_type(self):
        assert isinstance(ppm_color_temperature_estimate(_RED), float)

    def test_exact_1_for_pure_red(self):
        # 1x1-red: red=255, blue=0 → (255-0)/255 = 1.0
        assert ppm_color_temperature_estimate(_RED) == 1.0

    def test_zero_for_balanced_rgbw(self):
        # 2x2-rgbw: balanced R/G/B/W → red_mean == blue_mean
        assert ppm_color_temperature_estimate(_RGBW) == 0.0

    def test_zero_for_gradient(self):
        assert ppm_color_temperature_estimate(_GRAD) == 0.0

    def test_bounded(self):
        result = ppm_color_temperature_estimate(_RED)
        assert -1.0 <= result <= 1.0

    def test_consistent(self):
        assert ppm_color_temperature_estimate(_RED) == ppm_color_temperature_estimate(_RED)


class TestPpmChannelMeanStd:
    def test_return_type(self):
        assert isinstance(ppm_channel_mean_std(_RED), float)

    def test_nonzero_for_pure_red(self):
        # 1x1-red: [255, 0, 0] → very unbalanced channels
        result = ppm_channel_mean_std(_RED)
        assert abs(result - 120.208153) < 0.001

    def test_zero_for_balanced_rgbw(self):
        # 2x2-rgbw: R=G=B on average → std = 0
        assert ppm_channel_mean_std(_RGBW) == 0.0

    def test_zero_for_gradient(self):
        assert ppm_channel_mean_std(_GRAD) == 0.0

    def test_nonnegative(self):
        assert ppm_channel_mean_std(_RED) >= 0.0

    def test_consistent(self):
        assert ppm_channel_mean_std(_RED) == ppm_channel_mean_std(_RED)
