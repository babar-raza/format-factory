"""Tests for PGM grayscale_variance function (rnext38)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import grayscale_variance, write_pgm, PgmError


def _make_pgm(pixels: list[int], width: int, height: int, maxval: int = 255) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".pgm", delete=False)
    tmp.close()
    write_pgm(pixels, width, height, maxval, tmp.name)
    return tmp.name


class TestGrayscaleVariance:
    def test_uniform_image_zero_variance(self):
        # All pixels same value → variance = 0
        path = _make_pgm([100, 100, 100, 100], 2, 2)
        try:
            assert grayscale_variance(path) == 0.0
        finally:
            os.unlink(path)

    def test_two_value_image(self):
        # [0, 255, 0, 255] → mean=127.5, variance = 4 * (127.5^2) / 4 = 127.5^2
        path = _make_pgm([0, 255, 0, 255], 2, 2)
        try:
            result = grayscale_variance(path)
            assert abs(result - 127.5 ** 2) < 1e-6
        finally:
            os.unlink(path)

    def test_simple_values(self):
        # [1, 3] → mean=2, variance = ((1-2)^2 + (3-2)^2) / 2 = 1.0
        path = _make_pgm([1, 3], 2, 1, maxval=10)
        try:
            assert grayscale_variance(path) == 1.0
        finally:
            os.unlink(path)

    def test_single_pixel(self):
        # Single pixel → variance = 0
        path = _make_pgm([128], 1, 1)
        try:
            assert grayscale_variance(path) == 0.0
        finally:
            os.unlink(path)

    def test_returns_float(self):
        path = _make_pgm([10, 20, 30], 3, 1, maxval=255)
        try:
            result = grayscale_variance(path)
            assert isinstance(result, float)
            assert result >= 0.0
        finally:
            os.unlink(path)

    def test_nonexistent_raises(self):
        with pytest.raises(Exception):
            grayscale_variance("/nonexistent/file.pgm")
