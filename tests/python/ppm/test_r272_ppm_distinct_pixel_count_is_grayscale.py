"""Tests for ppm_distinct_pixel_count and ppm_is_grayscale (Sprint 62)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from ppm.ppm_parser import ppm_distinct_pixel_count, ppm_is_grayscale

PPM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ppm" / "valid"


class TestPpmDistinctPixelCount:
    def test_1x1_red(self):
        assert ppm_distinct_pixel_count(PPM / "1x1-red.ppm") == 1

    def test_2x2_rgbw(self):
        assert ppm_distinct_pixel_count(PPM / "2x2-rgbw.ppm") == 4

    def test_3x1_gradient(self):
        assert ppm_distinct_pixel_count(PPM / "3x1-gradient.ppm") == 3

    def test_returns_int(self):
        assert isinstance(ppm_distinct_pixel_count(PPM / "1x1-red.ppm"), int)

    def test_positive(self):
        for f in ["1x1-red.ppm", "2x2-rgbw.ppm", "3x1-gradient.ppm"]:
            assert ppm_distinct_pixel_count(PPM / f) > 0


class TestPpmIsGrayscale:
    def test_1x1_red_not_grayscale(self):
        assert ppm_is_grayscale(PPM / "1x1-red.ppm") is False

    def test_2x2_rgbw_not_grayscale(self):
        assert ppm_is_grayscale(PPM / "2x2-rgbw.ppm") is False

    def test_3x1_gradient_is_grayscale(self):
        assert ppm_is_grayscale(PPM / "3x1-gradient.ppm") is True

    def test_returns_bool(self):
        assert isinstance(ppm_is_grayscale(PPM / "1x1-red.ppm"), bool)

    def test_false_for_red_pixel(self):
        assert ppm_is_grayscale(PPM / "1x1-red.ppm") is False
