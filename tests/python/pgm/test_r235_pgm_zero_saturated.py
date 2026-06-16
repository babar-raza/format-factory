"""Tests for pgm_zero_pixel_count and pgm_saturated_pixel_count (Sprint 25)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import pgm_zero_pixel_count, pgm_saturated_pixel_count, write_pgm


def _make_pgm(tmp_path, name, pixels, width, height, maxval=255):
    p = tmp_path / f"{name}.pgm"
    write_pgm(pixels, width, height, maxval, str(p))
    return str(p)


class TestPgmZeroPixelCount:
    def test_no_zeros(self, tmp_path):
        p = _make_pgm(tmp_path, "nz", [100, 150, 200, 250], 2, 2)
        assert pgm_zero_pixel_count(p) == 0

    def test_all_zeros(self, tmp_path):
        p = _make_pgm(tmp_path, "az", [0, 0, 0, 0], 2, 2)
        assert pgm_zero_pixel_count(p) == 4

    def test_one_zero(self, tmp_path):
        p = _make_pgm(tmp_path, "oz", [0, 100, 200, 255], 2, 2)
        assert pgm_zero_pixel_count(p) == 1

    def test_return_type(self, tmp_path):
        p = _make_pgm(tmp_path, "rt", [50, 100], 2, 1)
        assert isinstance(pgm_zero_pixel_count(p), int)

    def test_two_zeros(self, tmp_path):
        p = _make_pgm(tmp_path, "tz", [0, 50, 0, 200], 2, 2)
        assert pgm_zero_pixel_count(p) == 2


class TestPgmSaturatedPixelCount:
    def test_all_saturated(self, tmp_path):
        p = _make_pgm(tmp_path, "as", [255, 255, 255, 255], 2, 2)
        assert pgm_saturated_pixel_count(p) == 4

    def test_none_saturated(self, tmp_path):
        p = _make_pgm(tmp_path, "ns", [0, 100, 200, 254], 2, 2)
        assert pgm_saturated_pixel_count(p) == 0

    def test_one_saturated(self, tmp_path):
        p = _make_pgm(tmp_path, "os", [100, 200, 255, 50], 2, 2)
        assert pgm_saturated_pixel_count(p) == 1

    def test_return_type(self, tmp_path):
        p = _make_pgm(tmp_path, "rt2", [255], 1, 1)
        assert isinstance(pgm_saturated_pixel_count(p), int)

    def test_two_saturated(self, tmp_path):
        p = _make_pgm(tmp_path, "ts2", [255, 100, 255, 50], 2, 2)
        assert pgm_saturated_pixel_count(p) == 2
