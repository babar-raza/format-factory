"""Tests for ppm_channel_range and ppm_saturation_estimate (Sprint 21)."""
import pytest
from src.python.ppm import write_ppm, ppm_channel_range, ppm_saturation_estimate


def _make_ppm(tmp_path, pixels, width, height, maxval=255):
    p = tmp_path / "test.ppm"
    write_ppm(pixels, width, height, maxval, str(p))
    return str(p)


class TestPpmChannelRange:
    def test_uniform_color(self, tmp_path):
        pixels = [(100, 100, 100)] * 4
        path = _make_ppm(tmp_path, pixels, 2, 2)
        result = ppm_channel_range(path)
        assert result == {"red": 0, "green": 0, "blue": 0}

    def test_varied_red(self, tmp_path):
        pixels = [(0, 50, 50), (255, 50, 50)]
        path = _make_ppm(tmp_path, pixels, 2, 1)
        result = ppm_channel_range(path)
        assert result["red"] == 255
        assert result["green"] == 0

    def test_return_type(self, tmp_path):
        pixels = [(10, 20, 30)]
        path = _make_ppm(tmp_path, pixels, 1, 1)
        result = ppm_channel_range(path)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"red", "green", "blue"}

    def test_all_channels_vary(self, tmp_path):
        pixels = [(0, 0, 0), (255, 128, 64)]
        path = _make_ppm(tmp_path, pixels, 2, 1)
        result = ppm_channel_range(path)
        assert result["red"] == 255
        assert result["green"] == 128
        assert result["blue"] == 64

    def test_single_pixel(self, tmp_path):
        pixels = [(42, 84, 126)]
        path = _make_ppm(tmp_path, pixels, 1, 1)
        result = ppm_channel_range(path)
        assert result == {"red": 0, "green": 0, "blue": 0}


class TestPpmSaturationEstimate:
    def test_grayscale(self, tmp_path):
        pixels = [(100, 100, 100)] * 4
        path = _make_ppm(tmp_path, pixels, 2, 2)
        assert ppm_saturation_estimate(path) == 0.0

    def test_pure_red(self, tmp_path):
        pixels = [(255, 0, 0)] * 2
        path = _make_ppm(tmp_path, pixels, 2, 1)
        assert ppm_saturation_estimate(path) == 255.0

    def test_mixed(self, tmp_path):
        pixels = [(200, 100, 50), (100, 100, 100)]
        path = _make_ppm(tmp_path, pixels, 2, 1)
        s = ppm_saturation_estimate(path)
        assert s > 0.0

    def test_return_type(self, tmp_path):
        pixels = [(0, 0, 0)]
        path = _make_ppm(tmp_path, pixels, 1, 1)
        assert isinstance(ppm_saturation_estimate(path), float)

    def test_non_negative(self, tmp_path):
        pixels = [(50, 100, 150)]
        path = _make_ppm(tmp_path, pixels, 1, 1)
        assert ppm_saturation_estimate(path) >= 0.0
