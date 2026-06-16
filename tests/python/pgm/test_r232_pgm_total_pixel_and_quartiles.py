"""Tests for pgm_total_pixel_count and pgm_brightness_quartiles.

Product deepening: PGM analytics — TC-H3-002-PGM / PDC-PGM-PIXEL-COUNT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_total_pixel_count,
    pgm_brightness_quartiles,
    write_pgm,
)


def _make_pgm(tmp_path, name, pixels, w, h, maxval=255):
    path = tmp_path / f"{name}.pgm"
    write_pgm(pixels, w, h, maxval, str(path))
    return path


class TestPgmTotalPixelCount:
    def test_1x1(self, tmp_path):
        f = _make_pgm(tmp_path, "1x1", [100], 1, 1)
        assert pgm_total_pixel_count(f) == 1

    def test_2x3(self, tmp_path):
        pixels = [10, 20, 30, 40, 50, 60]
        f = _make_pgm(tmp_path, "2x3", pixels, 3, 2)
        assert pgm_total_pixel_count(f) == 6

    def test_4x4(self, tmp_path):
        pixels = list(range(16))
        f = _make_pgm(tmp_path, "4x4", pixels, 4, 4)
        assert pgm_total_pixel_count(f) == 16

    def test_returns_int(self, tmp_path):
        f = _make_pgm(tmp_path, "type", [0], 1, 1)
        assert isinstance(pgm_total_pixel_count(f), int)

    def test_large_image(self, tmp_path):
        pixels = [128] * 100
        f = _make_pgm(tmp_path, "large", pixels, 10, 10)
        assert pgm_total_pixel_count(f) == 100


class TestPgmBrightnessQuartiles:
    def test_uniform_image(self, tmp_path):
        pixels = [128] * 4
        f = _make_pgm(tmp_path, "uniform", pixels, 2, 2)
        result = pgm_brightness_quartiles(f)
        assert result["q25"] == 128
        assert result["q50"] == 128
        assert result["q75"] == 128

    def test_gradient(self, tmp_path):
        pixels = list(range(100))
        f = _make_pgm(tmp_path, "gradient", pixels, 10, 10)
        result = pgm_brightness_quartiles(f)
        assert result["q25"] == 25
        assert result["q50"] == 50
        assert result["q75"] == 75

    def test_returns_dict(self, tmp_path):
        f = _make_pgm(tmp_path, "dict", [10, 20, 30, 40], 2, 2)
        result = pgm_brightness_quartiles(f)
        assert isinstance(result, dict)
        assert "q25" in result and "q50" in result and "q75" in result

    def test_ordering(self, tmp_path):
        pixels = [0, 50, 100, 150, 200, 250, 10, 20, 30]
        f = _make_pgm(tmp_path, "order", pixels, 3, 3)
        result = pgm_brightness_quartiles(f)
        assert result["q25"] <= result["q50"] <= result["q75"]

    def test_all_zeros(self, tmp_path):
        pixels = [0] * 4
        f = _make_pgm(tmp_path, "zeros", pixels, 2, 2)
        result = pgm_brightness_quartiles(f)
        assert result["q25"] == 0
        assert result["q50"] == 0
        assert result["q75"] == 0

    def test_returns_ints(self, tmp_path):
        f = _make_pgm(tmp_path, "types", [10, 20, 30, 40], 2, 2)
        result = pgm_brightness_quartiles(f)
        assert isinstance(result["q25"], int)
        assert isinstance(result["q50"], int)
        assert isinstance(result["q75"], int)
