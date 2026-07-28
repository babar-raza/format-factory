"""
test_r154_ppm_dimensions.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT12-001
Added: 2026-06-09

Tests for PPM get_dimensions function.
Authority: P5 (SAL-PPM-00001: P3 magic, SAL-PPM-00002: P6 magic)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import get_dimensions, write_ppm, PpmError


def _make_ppm(tmp_path: Path, width: int, height: int, maxval: int, pixels: list[tuple[int, int, int]]) -> Path:
    """Create a temporary PPM file."""
    p = tmp_path / "test.ppm"
    write_ppm(pixels, width, height, maxval, p)
    return p


class TestGetDimensions:
    """get_dimensions: return (width, height) of a PPM image."""

    def test_basic_dimensions(self, tmp_path):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                  (128, 128, 128), (0, 0, 0), (255, 255, 255)]
        p = _make_ppm(tmp_path, 3, 2, 255, pixels)
        assert get_dimensions(p) == (3, 2)

    def test_single_pixel(self, tmp_path):
        p = _make_ppm(tmp_path, 1, 1, 255, [(100, 200, 50)])
        assert get_dimensions(p) == (1, 1)

    def test_square_image(self, tmp_path):
        pixels = [(i, i, i) for i in range(4)]
        p = _make_ppm(tmp_path, 2, 2, 255, pixels)
        assert get_dimensions(p) == (2, 2)

    def test_wide_image(self, tmp_path):
        pixels = [(0, 0, 0)] * 10
        p = _make_ppm(tmp_path, 10, 1, 255, pixels)
        assert get_dimensions(p) == (10, 1)

    def test_tall_image(self, tmp_path):
        pixels = [(255, 255, 255)] * 8
        p = _make_ppm(tmp_path, 1, 8, 255, pixels)
        assert get_dimensions(p) == (1, 8)

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(PpmError):
            get_dimensions(tmp_path / "nonexistent.ppm")

    def test_dimensions_match_write_params(self, tmp_path):
        w, h = 7, 3
        pixels = [(10, 20, 30)] * (w * h)
        p = _make_ppm(tmp_path, w, h, 255, pixels)
        assert get_dimensions(p) == (w, h)
