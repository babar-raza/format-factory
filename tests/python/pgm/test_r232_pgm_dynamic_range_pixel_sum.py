"""Tests for pgm_dynamic_range and pgm_pixel_sum (Sprint 21)."""
import pytest
from src.python.pgm import write_pgm, pgm_dynamic_range, pgm_pixel_sum


@pytest.fixture
def tmp_pgm(tmp_path):
    def _make(pixels, width, height, maxval=255):
        p = tmp_path / "test.pgm"
        write_pgm(pixels, width, height, maxval, str(p))
        return str(p)
    return _make


class TestPgmDynamicRange:
    def test_uniform(self, tmp_pgm):
        path = tmp_pgm([100, 100, 100, 100], 2, 2)
        assert pgm_dynamic_range(path) == 0

    def test_full_range(self, tmp_pgm):
        path = tmp_pgm([0, 255], 2, 1)
        assert pgm_dynamic_range(path) == 255

    def test_partial_range(self, tmp_pgm):
        path = tmp_pgm([50, 100, 150], 3, 1)
        assert pgm_dynamic_range(path) == 100

    def test_return_type(self, tmp_pgm):
        path = tmp_pgm([10, 20], 2, 1)
        assert isinstance(pgm_dynamic_range(path), int)

    def test_non_negative(self, tmp_pgm):
        path = tmp_pgm([200, 50], 2, 1)
        assert pgm_dynamic_range(path) >= 0


class TestPgmPixelSum:
    def test_zeros(self, tmp_pgm):
        path = tmp_pgm([0, 0, 0, 0], 2, 2)
        assert pgm_pixel_sum(path) == 0

    def test_known_sum(self, tmp_pgm):
        path = tmp_pgm([10, 20, 30], 3, 1)
        assert pgm_pixel_sum(path) == 60

    def test_single_pixel(self, tmp_pgm):
        path = tmp_pgm([42], 1, 1)
        assert pgm_pixel_sum(path) == 42

    def test_return_type(self, tmp_pgm):
        path = tmp_pgm([1, 2], 2, 1)
        assert isinstance(pgm_pixel_sum(path), int)

    def test_max_values(self, tmp_pgm):
        path = tmp_pgm([255, 255], 2, 1)
        assert pgm_pixel_sum(path) == 510
