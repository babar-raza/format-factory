"""Dogfood: PPM write → parse → analytics → grayscale pipeline.

Demonstrates: create PPM pixels → write to disk → parse → dimensions → average color → grayscale conversion.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    write_ppm,
    parse_ppm_strict,
    get_dimensions,
    average_color,
    to_grayscale,
    PpmImage,
)


def _make_ppm_file(tmp_path: Path) -> Path:
    """Create a 4x3 PPM image with known pixel data."""
    pixels = [
        # Row 0: red gradient
        (255, 0, 0), (200, 0, 0), (150, 0, 0), (100, 0, 0),
        # Row 1: green gradient
        (0, 255, 0), (0, 200, 0), (0, 150, 0), (0, 100, 0),
        # Row 2: blue gradient
        (0, 0, 255), (0, 0, 200), (0, 0, 150), (0, 0, 100),
    ]
    p = tmp_path / "gradient.ppm"
    write_ppm(pixels, width=4, height=3, maxval=255, file_path=str(p))
    return p


class TestDogfoodPpmImagePipeline:
    @pytest.fixture
    def ppm_file(self, tmp_path):
        return _make_ppm_file(tmp_path)

    def test_write_creates_file(self, ppm_file):
        """PPM file is created on disk."""
        assert ppm_file.exists()
        assert ppm_file.stat().st_size > 0

    def test_parse_roundtrip(self, ppm_file):
        """Written PPM can be parsed back."""
        img = parse_ppm_strict(str(ppm_file))
        assert isinstance(img, PpmImage)
        assert img.width == 4
        assert img.height == 3

    def test_dimensions(self, ppm_file):
        """Dimensions are correct."""
        w, h = get_dimensions(str(ppm_file))
        assert w == 4
        assert h == 3

    def test_pixel_count(self, ppm_file):
        """Pixel count matches width * height."""
        img = parse_ppm_strict(str(ppm_file))
        assert len(img.pixels) == 12  # 4 * 3

    def test_average_color(self, ppm_file):
        """Average color is computed correctly."""
        r, g, b = average_color(str(ppm_file))
        assert isinstance(r, float)
        assert isinstance(g, float)
        assert isinstance(b, float)
        # With our gradient data, all channels should have non-zero averages
        assert r > 0
        assert g > 0
        assert b > 0

    def test_grayscale_conversion(self, ppm_file, tmp_path):
        """Grayscale conversion produces a valid output file."""
        gray_path = tmp_path / "gray.ppm"
        result = to_grayscale(str(ppm_file), str(gray_path))
        assert gray_path.exists()
        assert isinstance(result, dict)

    def test_maxval(self, ppm_file):
        """Max value is 255."""
        img = parse_ppm_strict(str(ppm_file))
        assert img.maxval == 255
