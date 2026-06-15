"""Tests for pgm_median_pixel_value function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_median_pixel_value, write_pgm, PgmError


@pytest.fixture
def tmp_pgm(tmp_path):
    """Helper to write a PGM file from pixels."""
    def _make(pixels, width, height, maxval=255):
        p = tmp_path / "test.pgm"
        write_pgm(pixels, width, height, maxval, str(p))
        return str(p)
    return _make


class TestPgmMedianPixelValue:
    def test_uniform_image(self, tmp_pgm):
        path = tmp_pgm([128, 128, 128, 128], 2, 2)
        assert pgm_median_pixel_value(path) == 128

    def test_odd_count_returns_middle(self, tmp_pgm):
        path = tmp_pgm([10, 50, 200], 3, 1)
        assert pgm_median_pixel_value(path) == 50

    def test_even_count_returns_lower_middle(self, tmp_pgm):
        path = tmp_pgm([10, 50, 100, 200], 4, 1)
        # Sorted: [10, 50, 100, 200], mid=2, lower middle = index 1 = 50
        assert pgm_median_pixel_value(path) == 50

    def test_all_black(self, tmp_pgm):
        path = tmp_pgm([0, 0, 0, 0, 0], 5, 1)
        assert pgm_median_pixel_value(path) == 0

    def test_all_white(self, tmp_pgm):
        path = tmp_pgm([255, 255, 255], 3, 1)
        assert pgm_median_pixel_value(path) == 255

    def test_two_values_returns_lower(self, tmp_pgm):
        path = tmp_pgm([100, 200], 2, 1)
        assert pgm_median_pixel_value(path) == 100

    def test_single_pixel(self, tmp_pgm):
        path = tmp_pgm([42], 1, 1)
        assert pgm_median_pixel_value(path) == 42

    def test_importable_from_package(self):
        from pgm import pgm_median_pixel_value as fn
        assert callable(fn)
