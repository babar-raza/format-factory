"""Tests for PPM is_grayscale function (rnext39)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import is_grayscale, write_ppm, PpmError


def _make_ppm(pixels: list[tuple[int, int, int]], width: int, height: int, maxval: int = 255) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False)
    tmp.close()
    write_ppm(pixels, width, height, maxval, tmp.name)
    return tmp.name


class TestIsGrayscale:
    def test_pure_gray_pixels(self):
        # All R==G==B
        path = _make_ppm([(100, 100, 100), (200, 200, 200)], 2, 1)
        try:
            assert is_grayscale(path) is True
        finally:
            os.unlink(path)

    def test_color_pixel(self):
        # R != G
        path = _make_ppm([(255, 0, 0)], 1, 1)
        try:
            assert is_grayscale(path) is False
        finally:
            os.unlink(path)

    def test_mixed_gray_and_color(self):
        path = _make_ppm([(128, 128, 128), (255, 0, 0)], 2, 1)
        try:
            assert is_grayscale(path) is False
        finally:
            os.unlink(path)

    def test_black_white_grayscale(self):
        path = _make_ppm([(0, 0, 0), (255, 255, 255)], 2, 1)
        try:
            assert is_grayscale(path) is True
        finally:
            os.unlink(path)

    def test_nonexistent_raises(self):
        with pytest.raises(Exception):
            is_grayscale("/nonexistent/file.ppm")
