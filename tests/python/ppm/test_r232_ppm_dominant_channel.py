"""Tests for ppm_dominant_channel and ppm_min_max_brightness.

Product deepening: PPM analytics — TC-H3-002-PPM / PDC-PPM-DOMINANT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_dominant_channel,
    ppm_min_max_brightness,
    write_ppm,
)


def _make_ppm(tmp_path, name, pixels, w, h, maxval=255):
    path = tmp_path / f"{name}.ppm"
    write_ppm(pixels, w, h, maxval, str(path))
    return path


class TestPpmDominantChannel:
    def test_red_dominant(self, tmp_path):
        pixels = [(255, 0, 0), (200, 0, 0)]
        f = _make_ppm(tmp_path, "red", pixels, 2, 1)
        assert ppm_dominant_channel(f) == "red"

    def test_green_dominant(self, tmp_path):
        pixels = [(0, 255, 0), (0, 200, 0)]
        f = _make_ppm(tmp_path, "green", pixels, 2, 1)
        assert ppm_dominant_channel(f) == "green"

    def test_blue_dominant(self, tmp_path):
        pixels = [(0, 0, 255), (0, 0, 200)]
        f = _make_ppm(tmp_path, "blue", pixels, 2, 1)
        assert ppm_dominant_channel(f) == "blue"

    def test_tie_favors_red(self, tmp_path):
        pixels = [(100, 100, 100)]
        f = _make_ppm(tmp_path, "tie", pixels, 1, 1)
        assert ppm_dominant_channel(f) == "red"

    def test_returns_string(self, tmp_path):
        pixels = [(10, 20, 30)]
        f = _make_ppm(tmp_path, "type", pixels, 1, 1)
        assert isinstance(ppm_dominant_channel(f), str)

    def test_valid_values(self, tmp_path):
        pixels = [(50, 100, 150)]
        f = _make_ppm(tmp_path, "val", pixels, 1, 1)
        assert ppm_dominant_channel(f) in ("red", "green", "blue")


class TestPpmMinMaxBrightness:
    def test_single_pixel(self, tmp_path):
        pixels = [(100, 100, 100)]
        f = _make_ppm(tmp_path, "single", pixels, 1, 1)
        result = ppm_min_max_brightness(f)
        assert result["min"] == result["max"]
        assert abs(result["min"] - 100.0) < 0.01

    def test_two_pixels(self, tmp_path):
        pixels = [(0, 0, 0), (255, 255, 255)]
        f = _make_ppm(tmp_path, "bw", pixels, 2, 1)
        result = ppm_min_max_brightness(f)
        assert result["min"] == 0.0
        assert abs(result["max"] - 255.0) < 0.01

    def test_returns_dict(self, tmp_path):
        pixels = [(10, 20, 30)]
        f = _make_ppm(tmp_path, "dict", pixels, 1, 1)
        result = ppm_min_max_brightness(f)
        assert isinstance(result, dict)
        assert "min" in result
        assert "max" in result

    def test_min_leq_max(self, tmp_path):
        pixels = [(50, 100, 200), (200, 50, 100)]
        f = _make_ppm(tmp_path, "leq", pixels, 2, 1)
        result = ppm_min_max_brightness(f)
        assert result["min"] <= result["max"]

    def test_brightness_formula(self, tmp_path):
        pixels = [(100, 0, 0)]
        f = _make_ppm(tmp_path, "formula", pixels, 1, 1)
        result = ppm_min_max_brightness(f)
        expected = 0.299 * 100
        assert abs(result["min"] - expected) < 0.01
