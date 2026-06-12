"""
test_r188_ppm_red_channel_average.py — Tests for ppm_red_channel_average function.

Sprint: product-deepening-rnext56
"""
import pytest
from pathlib import Path
from src.python.ppm import ppm_red_channel_average, write_ppm, PpmError


def _make_ppm(tmp_path: Path, pixels: list, width: int, height: int, maxval: int = 255) -> Path:
    p = tmp_path / "test.ppm"
    write_ppm(pixels, width, height, maxval, p)
    return p


def test_all_zero_red_returns_zero(tmp_path):
    """All pixels have red=0 → average 0.0."""
    p = _make_ppm(tmp_path, [(0, 100, 200), (0, 50, 50)], 2, 1)
    assert ppm_red_channel_average(p) == 0.0


def test_all_max_red_returns_maxval(tmp_path):
    """All pixels have red=255 → average 255.0."""
    p = _make_ppm(tmp_path, [(255, 0, 0), (255, 100, 100)], 2, 1)
    assert ppm_red_channel_average(p) == 255.0


def test_mixed_red_channels(tmp_path):
    """Mixed red values: (100, ...) and (200, ...) → average 150.0."""
    p = _make_ppm(tmp_path, [(100, 50, 50), (200, 50, 50)], 2, 1)
    assert ppm_red_channel_average(p) == pytest.approx(150.0)


def test_single_pixel(tmp_path):
    """Single pixel → average equals its red channel value."""
    p = _make_ppm(tmp_path, [(77, 88, 99)], 1, 1)
    assert ppm_red_channel_average(p) == 77.0


def test_red_channel_unaffected_by_green_blue(tmp_path):
    """Only red channel is averaged; green/blue values are ignored."""
    p = _make_ppm(tmp_path, [(50, 255, 255), (50, 0, 0)], 2, 1)
    assert ppm_red_channel_average(p) == 50.0


def test_result_is_float(tmp_path):
    """Result is always a float."""
    p = _make_ppm(tmp_path, [(100, 0, 0), (200, 0, 0)], 2, 1)
    result = ppm_red_channel_average(p)
    assert isinstance(result, float)
