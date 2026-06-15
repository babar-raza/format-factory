"""Tests for ppm_green_channel_average().

Sprint: product-deepening-rnext83
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_green_channel_average

PPM_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmGreenChannelAverage:
    def test_import(self):
        assert callable(ppm_green_channel_average)

    def test_red_image_has_zero_green(self):
        result = ppm_green_channel_average(PPM_SAMPLES / "1x1-red.ppm")
        assert result == 0.0

    def test_rgbw_image_green_average(self):
        result = ppm_green_channel_average(PPM_SAMPLES / "2x2-rgbw.ppm")
        assert result == 127.5

    def test_gradient_image_green_average(self):
        result = ppm_green_channel_average(PPM_SAMPLES / "3x1-gradient.ppm")
        assert abs(result - 127.667) < 0.01

    def test_returns_float(self):
        result = ppm_green_channel_average(PPM_SAMPLES / "1x1-red.ppm")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for sample in PPM_SAMPLES.iterdir():
            if sample.suffix == ".ppm":
                assert ppm_green_channel_average(sample) >= 0.0
