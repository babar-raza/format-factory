"""
test_r157_ppm_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT17-001
Added: 2026-06-10

Tests for PPM pixel_count and average_color functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import pixel_count, average_color, write_ppm, PpmError

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPixelCount:
    def test_1x1(self):
        assert pixel_count(_SAMPLES / "1x1-red.ppm") == 1

    def test_2x2(self):
        assert pixel_count(_SAMPLES / "2x2-rgbw.ppm") == 4

    def test_3x1(self):
        assert pixel_count(_SAMPLES / "3x1-gradient.ppm") == 3

    def test_nonexistent_file(self):
        with pytest.raises(PpmError):
            pixel_count(_SAMPLES / "ghost.ppm")

    def test_written_file(self, tmp_path):
        p = tmp_path / "test.ppm"
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        write_ppm(pixels, 3, 2, 255, p)
        assert pixel_count(p) == 6


class TestAverageColor:
    def test_1x1_red(self):
        avg = average_color(_SAMPLES / "1x1-red.ppm")
        assert avg[0] == 255.0
        assert avg[1] == 0.0
        assert avg[2] == 0.0

    def test_uniform_color(self, tmp_path):
        p = tmp_path / "uniform.ppm"
        pixels = [(100, 200, 50)] * 4
        write_ppm(pixels, 2, 2, 255, p)
        avg = average_color(p)
        assert avg == (100.0, 200.0, 50.0)

    def test_mixed_colors(self, tmp_path):
        p = tmp_path / "mixed.ppm"
        pixels = [(0, 0, 0), (200, 200, 200)]
        write_ppm(pixels, 2, 1, 255, p)
        avg = average_color(p)
        assert avg == (100.0, 100.0, 100.0)

    def test_nonexistent_file(self):
        with pytest.raises(PpmError):
            average_color(_SAMPLES / "ghost.ppm")

    def test_returns_tuple(self):
        avg = average_color(_SAMPLES / "1x1-red.ppm")
        assert isinstance(avg, tuple)
        assert len(avg) == 3
