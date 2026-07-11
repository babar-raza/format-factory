"""Tests for extended PPM color analytics (ppm_is_grayscale, channel ratios)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

RGBW = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"

from src.python.ppm.color_image import (
    ppm_is_grayscale,
    ppm_red_channel_ratio,
    ppm_green_channel_ratio,
    ppm_blue_channel_ratio,
)


class TestPpmIsGrayscale:
    def test_returns_bool(self):
        assert isinstance(ppm_is_grayscale(RGBW), bool)

    def test_rgbw_not_grayscale(self):
        # 2x2-rgbw has distinct R, G, B pixels
        assert ppm_is_grayscale(RGBW) is False

    def test_accepts_string_path(self):
        assert isinstance(ppm_is_grayscale(str(RGBW)), bool)


class TestPpmRedChannelRatio:
    def test_returns_float(self):
        assert isinstance(ppm_red_channel_ratio(RGBW), float)

    def test_in_unit_range(self):
        assert 0.0 <= ppm_red_channel_ratio(RGBW) <= 1.0

    def test_positive_for_rgbw(self):
        assert ppm_red_channel_ratio(RGBW) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(ppm_red_channel_ratio(str(RGBW)), float)


class TestPpmGreenChannelRatio:
    def test_returns_float(self):
        assert isinstance(ppm_green_channel_ratio(RGBW), float)

    def test_in_unit_range(self):
        assert 0.0 <= ppm_green_channel_ratio(RGBW) <= 1.0

    def test_positive_for_rgbw(self):
        assert ppm_green_channel_ratio(RGBW) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(ppm_green_channel_ratio(str(RGBW)), float)


class TestPpmBlueChannelRatio:
    def test_returns_float(self):
        assert isinstance(ppm_blue_channel_ratio(RGBW), float)

    def test_in_unit_range(self):
        assert 0.0 <= ppm_blue_channel_ratio(RGBW) <= 1.0

    def test_positive_for_rgbw(self):
        assert ppm_blue_channel_ratio(RGBW) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(ppm_blue_channel_ratio(str(RGBW)), float)


class TestChannelRatiosSumToOne:
    def test_channel_ratios_sum_to_one(self):
        r = ppm_red_channel_ratio(RGBW)
        g = ppm_green_channel_ratio(RGBW)
        b = ppm_blue_channel_ratio(RGBW)
        assert abs(r + g + b - 1.0) < 1e-9
