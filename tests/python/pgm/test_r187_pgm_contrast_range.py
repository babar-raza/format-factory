"""
Tests for pgm_contrast_range — dynamic range (max_gray - min_gray) of a PGM image.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT80-001
"""

import sys
import pytest

sys.path.insert(0, "src/python")

from pgm import pgm_contrast_range, write_pgm


def _make_pgm(pixels: list[int], width: int, height: int, tmp_path, maxval: int = 255, name: str = "test.pgm"):
    path = tmp_path / name
    write_pgm(pixels, width, height, maxval, path)
    return path


def test_full_range_0_to_255(tmp_path):
    # min=0, max=255 → range=255
    pixels = [0, 128, 255]
    path = _make_pgm(pixels, 3, 1, tmp_path)
    assert pgm_contrast_range(path) == 255


def test_uniform_image_range_zero(tmp_path):
    # All pixels the same → range=0
    pixels = [100, 100, 100, 100]
    path = _make_pgm(pixels, 2, 2, tmp_path)
    assert pgm_contrast_range(path) == 0


def test_two_pixel_values(tmp_path):
    pixels = [50, 150]
    path = _make_pgm(pixels, 2, 1, tmp_path)
    assert pgm_contrast_range(path) == 100


def test_single_pixel(tmp_path):
    pixels = [200]
    path = _make_pgm(pixels, 1, 1, tmp_path)
    assert pgm_contrast_range(path) == 0


def test_all_black(tmp_path):
    pixels = [0, 0, 0, 0]
    path = _make_pgm(pixels, 2, 2, tmp_path)
    assert pgm_contrast_range(path) == 0


def test_all_white_at_maxval(tmp_path):
    pixels = [255, 255, 255]
    path = _make_pgm(pixels, 3, 1, tmp_path)
    assert pgm_contrast_range(path) == 0


def test_small_range(tmp_path):
    pixels = [100, 101, 102, 103]
    path = _make_pgm(pixels, 2, 2, tmp_path)
    assert pgm_contrast_range(path) == 3


def test_maxval_16_range(tmp_path):
    # 4-bit depth image
    pixels = [0, 8, 16]
    path = _make_pgm(pixels, 3, 1, tmp_path, maxval=16)
    assert pgm_contrast_range(path) == 16


def test_returns_int(tmp_path):
    pixels = [10, 200]
    path = _make_pgm(pixels, 2, 1, tmp_path)
    result = pgm_contrast_range(path)
    assert isinstance(result, int)


def test_large_image_range(tmp_path):
    # 10x10 checkerboard with min=20, max=220
    pixels = [20 if (i + j) % 2 == 0 else 220 for i in range(10) for j in range(10)]
    path = _make_pgm(pixels, 10, 10, tmp_path)
    assert pgm_contrast_range(path) == 200
