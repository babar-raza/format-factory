"""Tests for QOI analytics deepening (R290O): center_pixel_brightness, edge_brightness, red_green_diff."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import qoi_center_pixel_brightness, qoi_edge_brightness, qoi_red_green_diff

SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"


def test_center_pixel_brightness_returns_float():
    result = qoi_center_pixel_brightness(SAMPLES / "1x1-red.qoi")
    assert isinstance(result, float)
    assert result >= 0.0


def test_center_pixel_brightness_gradient():
    result = qoi_center_pixel_brightness(SAMPLES / "4x1-gradient.qoi")
    assert isinstance(result, float)


def test_edge_brightness_returns_float():
    result = qoi_edge_brightness(SAMPLES / "2x2-black.qoi")
    assert isinstance(result, float)
    assert result >= 0.0


def test_edge_brightness_gradient():
    result = qoi_edge_brightness(SAMPLES / "4x1-gradient.qoi")
    assert isinstance(result, float)


def test_red_green_diff_returns_float():
    result = qoi_red_green_diff(SAMPLES / "1x1-red.qoi")
    assert isinstance(result, float)
    assert result >= 0.0


def test_red_green_diff_black():
    result = qoi_red_green_diff(SAMPLES / "2x2-black.qoi")
    assert isinstance(result, float)
    assert result == 0.0  # black has 0 in all channels
