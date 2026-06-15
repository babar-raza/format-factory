"""Tests for ppm_aspect_ratio function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_aspect_ratio, write_ppm


def _make_ppm(tmp_path, pixels, width, height, maxval=255):
    p = tmp_path / "test.ppm"
    write_ppm(pixels, width, height, maxval, str(p))
    return str(p)


class TestPpmAspectRatio:
    def test_square_image(self, tmp_path):
        pixels = [(0, 0, 0)] * 4
        path = _make_ppm(tmp_path, pixels, 2, 2)
        assert ppm_aspect_ratio(path) == pytest.approx(1.0)

    def test_landscape(self, tmp_path):
        pixels = [(0, 0, 0)] * 6
        path = _make_ppm(tmp_path, pixels, 3, 2)
        assert ppm_aspect_ratio(path) == pytest.approx(1.5)

    def test_portrait(self, tmp_path):
        pixels = [(0, 0, 0)] * 6
        path = _make_ppm(tmp_path, pixels, 2, 3)
        assert ppm_aspect_ratio(path) == pytest.approx(2 / 3)

    def test_wide_image(self, tmp_path):
        pixels = [(0, 0, 0)] * 10
        path = _make_ppm(tmp_path, pixels, 10, 1)
        assert ppm_aspect_ratio(path) == pytest.approx(10.0)

    def test_tall_image(self, tmp_path):
        pixels = [(0, 0, 0)] * 10
        path = _make_ppm(tmp_path, pixels, 1, 10)
        assert ppm_aspect_ratio(path) == pytest.approx(0.1)

    def test_single_pixel(self, tmp_path):
        pixels = [(128, 128, 128)]
        path = _make_ppm(tmp_path, pixels, 1, 1)
        assert ppm_aspect_ratio(path) == pytest.approx(1.0)

    def test_return_type_is_float(self, tmp_path):
        pixels = [(0, 0, 0)] * 4
        path = _make_ppm(tmp_path, pixels, 2, 2)
        assert isinstance(ppm_aspect_ratio(path), float)

    def test_importable_from_package(self):
        from ppm import ppm_aspect_ratio as fn
        assert callable(fn)
