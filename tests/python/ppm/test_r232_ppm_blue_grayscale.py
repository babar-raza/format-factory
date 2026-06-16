"""Tests for ppm_blue_channel_average and ppm_is_grayscale.

Product deepening: PPM analytics — TC-H3-002-PPM / PDC-PPM-BLUE-GRAY-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import write_ppm, ppm_blue_channel_average, ppm_is_grayscale


def _make_ppm(tmp_path, name, w, h, pixels):
    p = tmp_path / f"{name}.ppm"
    write_ppm(pixels, w, h, 255, str(p))
    return p


class TestPpmBlueChannelAverage:
    def test_uniform_blue(self, tmp_path):
        p = _make_ppm(tmp_path, "blue", 2, 1, [(0, 0, 100), (0, 0, 200)])
        assert ppm_blue_channel_average(p) == 150.0

    def test_zero_blue(self, tmp_path):
        p = _make_ppm(tmp_path, "no_blue", 2, 1, [(255, 0, 0), (0, 255, 0)])
        assert ppm_blue_channel_average(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_ppm(tmp_path, "ft", 1, 1, [(10, 20, 30)])
        assert isinstance(ppm_blue_channel_average(p), float)

    def test_non_negative(self, tmp_path):
        p = _make_ppm(tmp_path, "nn", 1, 1, [(0, 0, 0)])
        assert ppm_blue_channel_average(p) >= 0.0

    def test_max_value(self, tmp_path):
        p = _make_ppm(tmp_path, "max", 1, 1, [(0, 0, 255)])
        assert ppm_blue_channel_average(p) == 255.0


class TestPpmIsGrayscale:
    def test_grayscale(self, tmp_path):
        p = _make_ppm(tmp_path, "gray", 2, 1, [(100, 100, 100), (200, 200, 200)])
        assert ppm_is_grayscale(p) is True

    def test_not_grayscale(self, tmp_path):
        p = _make_ppm(tmp_path, "color", 2, 1, [(255, 0, 0), (0, 255, 0)])
        assert ppm_is_grayscale(p) is False

    def test_returns_bool(self, tmp_path):
        p = _make_ppm(tmp_path, "bool_t", 1, 1, [(50, 50, 50)])
        assert isinstance(ppm_is_grayscale(p), bool)

    def test_single_pixel(self, tmp_path):
        p = _make_ppm(tmp_path, "one_px", 1, 1, [(128, 128, 128)])
        assert ppm_is_grayscale(p) is True

    def test_almost_gray(self, tmp_path):
        p = _make_ppm(tmp_path, "almost", 1, 1, [(100, 100, 101)])
        assert ppm_is_grayscale(p) is False
