"""
Tests for Sprint r310: ppm_is_multi_row, ppm_has_multi_channel_pixels.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_is_multi_row, ppm_has_multi_channel_pixels

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


# --- ppm_is_multi_row ---

def test_ppm_is_multi_row_1x1_red_false():
    assert ppm_is_multi_row(_PPM / "1x1-red.ppm") is False


def test_ppm_is_multi_row_2x2_rgbw_true():
    assert ppm_is_multi_row(_PPM / "2x2-rgbw.ppm") is True


def test_ppm_is_multi_row_3x1_gradient_false():
    assert ppm_is_multi_row(_PPM / "3x1-gradient.ppm") is False


def test_ppm_is_multi_row_returns_bool_1x1():
    assert isinstance(ppm_is_multi_row(_PPM / "1x1-red.ppm"), bool)


def test_ppm_is_multi_row_returns_bool_2x2():
    assert isinstance(ppm_is_multi_row(_PPM / "2x2-rgbw.ppm"), bool)


def test_ppm_is_multi_row_all_three_distinct():
    results = [
        ppm_is_multi_row(_PPM / "1x1-red.ppm"),
        ppm_is_multi_row(_PPM / "2x2-rgbw.ppm"),
        ppm_is_multi_row(_PPM / "3x1-gradient.ppm"),
    ]
    assert results == [False, True, False]


# --- ppm_has_multi_channel_pixels ---

def test_ppm_has_multi_channel_pixels_1x1_red_false():
    # (255, 0, 0) — only R is nonzero
    assert ppm_has_multi_channel_pixels(_PPM / "1x1-red.ppm") is False


def test_ppm_has_multi_channel_pixels_2x2_rgbw_true():
    # includes (255, 255, 255) — all three channels nonzero
    assert ppm_has_multi_channel_pixels(_PPM / "2x2-rgbw.ppm") is True


def test_ppm_has_multi_channel_pixels_3x1_gradient_true():
    # includes (128, 128, 128) and (255, 255, 255) — multi-channel
    assert ppm_has_multi_channel_pixels(_PPM / "3x1-gradient.ppm") is True


def test_ppm_has_multi_channel_pixels_returns_bool_1x1():
    assert isinstance(ppm_has_multi_channel_pixels(_PPM / "1x1-red.ppm"), bool)


def test_ppm_has_multi_channel_pixels_returns_bool_2x2():
    assert isinstance(ppm_has_multi_channel_pixels(_PPM / "2x2-rgbw.ppm"), bool)


def test_ppm_has_multi_channel_pixels_all_three():
    results = [
        ppm_has_multi_channel_pixels(_PPM / "1x1-red.ppm"),
        ppm_has_multi_channel_pixels(_PPM / "2x2-rgbw.ppm"),
        ppm_has_multi_channel_pixels(_PPM / "3x1-gradient.ppm"),
    ]
    assert results == [False, True, True]
