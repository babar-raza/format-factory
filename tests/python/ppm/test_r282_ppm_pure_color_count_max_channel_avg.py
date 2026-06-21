"""Tests for ppm_pure_color_count and ppm_max_channel_avg (Sprint 72)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from ppm.ppm_parser import ppm_pure_color_count, ppm_max_channel_avg

PPM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ppm" / "valid"


class TestPpmPureColorCount:
    def test_single_red(self):
        assert ppm_pure_color_count(PPM / "1x1-red.ppm") == 1

    def test_rgbw_three(self):
        assert ppm_pure_color_count(PPM / "2x2-rgbw.ppm") == 3

    def test_gradient_none(self):
        assert ppm_pure_color_count(PPM / "3x1-gradient.ppm") == 0

    def test_returns_int(self):
        assert isinstance(ppm_pure_color_count(PPM / "1x1-red.ppm"), int)

    def test_nonnegative(self):
        for f in ["1x1-red.ppm", "2x2-rgbw.ppm", "3x1-gradient.ppm"]:
            assert ppm_pure_color_count(PPM / f) >= 0


class TestPpmMaxChannelAvg:
    def test_red_pixel(self):
        assert abs(ppm_max_channel_avg(PPM / "1x1-red.ppm") - 255.0) < 0.01

    def test_rgbw(self):
        assert abs(ppm_max_channel_avg(PPM / "2x2-rgbw.ppm") - 127.5) < 0.01

    def test_gradient(self):
        assert abs(ppm_max_channel_avg(PPM / "3x1-gradient.ppm") - 127.67) < 0.1

    def test_returns_float(self):
        assert isinstance(ppm_max_channel_avg(PPM / "1x1-red.ppm"), float)

    def test_nonnegative(self):
        for f in ["1x1-red.ppm", "2x2-rgbw.ppm", "3x1-gradient.ppm"]:
            assert ppm_max_channel_avg(PPM / f) >= 0.0
