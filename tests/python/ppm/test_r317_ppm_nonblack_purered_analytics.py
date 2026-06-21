"""
Tests for Sprint r317: ppm_non_black_pixel_count, ppm_has_pure_red_pixel.
Uses sample files from samples/by-format/ppm/valid/.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_non_black_pixel_count, ppm_has_pure_red_pixel

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


# --- ppm_non_black_pixel_count ---

def test_ppm_non_black_pixel_count_1x1_red():
    assert ppm_non_black_pixel_count(_PPM / "1x1-red.ppm") == 1


def test_ppm_non_black_pixel_count_2x2_rgbw():
    assert ppm_non_black_pixel_count(_PPM / "2x2-rgbw.ppm") == 4


def test_ppm_non_black_pixel_count_3x1_gradient():
    # (0,0,0) is black; (128,128,128) and (255,255,255) are non-black
    assert ppm_non_black_pixel_count(_PPM / "3x1-gradient.ppm") == 2


def test_ppm_non_black_pixel_count_returns_int_1x1():
    assert isinstance(ppm_non_black_pixel_count(_PPM / "1x1-red.ppm"), int)


def test_ppm_non_black_pixel_count_returns_int_2x2():
    assert isinstance(ppm_non_black_pixel_count(_PPM / "2x2-rgbw.ppm"), int)


def test_ppm_non_black_pixel_count_all_three_distinct():
    results = [
        ppm_non_black_pixel_count(_PPM / "1x1-red.ppm"),
        ppm_non_black_pixel_count(_PPM / "2x2-rgbw.ppm"),
        ppm_non_black_pixel_count(_PPM / "3x1-gradient.ppm"),
    ]
    assert results == [1, 4, 2]


# --- ppm_has_pure_red_pixel ---

def test_ppm_has_pure_red_pixel_1x1_red_true():
    assert ppm_has_pure_red_pixel(_PPM / "1x1-red.ppm") is True


def test_ppm_has_pure_red_pixel_2x2_rgbw_true():
    assert ppm_has_pure_red_pixel(_PPM / "2x2-rgbw.ppm") is True


def test_ppm_has_pure_red_pixel_3x1_gradient_false():
    assert ppm_has_pure_red_pixel(_PPM / "3x1-gradient.ppm") is False


def test_ppm_has_pure_red_pixel_returns_bool_1x1():
    assert isinstance(ppm_has_pure_red_pixel(_PPM / "1x1-red.ppm"), bool)


def test_ppm_has_pure_red_pixel_returns_bool_gradient():
    assert isinstance(ppm_has_pure_red_pixel(_PPM / "3x1-gradient.ppm"), bool)


def test_ppm_has_pure_red_pixel_all_three():
    results = [
        ppm_has_pure_red_pixel(_PPM / "1x1-red.ppm"),
        ppm_has_pure_red_pixel(_PPM / "2x2-rgbw.ppm"),
        ppm_has_pure_red_pixel(_PPM / "3x1-gradient.ppm"),
    ]
    assert results == [True, True, False]
