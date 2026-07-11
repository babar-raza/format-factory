"""Tests for PPM image analytics extension (ppm_image_analytics.py)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_image_analytics import (
    ppm_has_single_pixel,
    ppm_has_single_row,
    ppm_has_single_column,
    ppm_is_high_depth,
    ppm_all_white,
    ppm_all_black,
)

SAMPLES = Path("samples/by-format/ppm/valid")
RED      = SAMPLES / "1x1-red.ppm"      # 1x1, maxval=255, pixels=[(255,0,0)]
RGBW     = SAMPLES / "2x2-rgbw.ppm"     # 2x2, maxval=255, 4 pixels
GRADIENT = SAMPLES / "3x1-gradient.ppm" # 3x1, maxval=255, [(0,0,0),(128,128,128),(255,255,255)]


# --- ppm_has_single_pixel ---

def test_has_single_pixel_red():
    assert ppm_has_single_pixel(RED) is True


def test_has_single_pixel_rgbw():
    assert ppm_has_single_pixel(RGBW) is False


def test_has_single_pixel_gradient():
    assert ppm_has_single_pixel(GRADIENT) is False


def test_has_single_pixel_returns_bool():
    assert isinstance(ppm_has_single_pixel(RED), bool)


# --- ppm_has_single_row ---

def test_has_single_row_red():
    # 1x1 → height=1 → True
    assert ppm_has_single_row(RED) is True


def test_has_single_row_gradient():
    # 3x1 → height=1 → True
    assert ppm_has_single_row(GRADIENT) is True


def test_has_single_row_rgbw():
    # 2x2 → height=2 → False
    assert ppm_has_single_row(RGBW) is False


def test_has_single_row_returns_bool():
    assert isinstance(ppm_has_single_row(RED), bool)


# --- ppm_has_single_column ---

def test_has_single_column_red():
    # 1x1 → width=1 → True
    assert ppm_has_single_column(RED) is True


def test_has_single_column_rgbw():
    # 2x2 → width=2 → False
    assert ppm_has_single_column(RGBW) is False


def test_has_single_column_gradient():
    # 3x1 → width=3 → False
    assert ppm_has_single_column(GRADIENT) is False


def test_has_single_column_returns_bool():
    assert isinstance(ppm_has_single_column(RED), bool)


# --- ppm_is_high_depth ---

def test_is_high_depth_red():
    # maxval=255 → not high depth
    assert ppm_is_high_depth(RED) is False


def test_is_high_depth_rgbw():
    assert ppm_is_high_depth(RGBW) is False


def test_is_high_depth_gradient():
    assert ppm_is_high_depth(GRADIENT) is False


def test_is_high_depth_returns_bool():
    assert isinstance(ppm_is_high_depth(RED), bool)


# --- ppm_all_white ---

def test_all_white_red():
    # (255,0,0) is not white
    assert ppm_all_white(RED) is False


def test_all_white_rgbw():
    # 2x2 has red, green, blue, white pixels — not all white
    assert ppm_all_white(RGBW) is False


def test_all_white_gradient():
    # gradient has black pixel — not all white
    assert ppm_all_white(GRADIENT) is False


def test_all_white_returns_bool():
    assert isinstance(ppm_all_white(RED), bool)


# --- ppm_all_black ---

def test_all_black_red():
    # (255,0,0) is not black
    assert ppm_all_black(RED) is False


def test_all_black_rgbw():
    # 2x2 has non-black pixels
    assert ppm_all_black(RGBW) is False


def test_all_black_gradient():
    # gradient has (128,128,128) and (255,255,255) — not all black
    assert ppm_all_black(GRADIENT) is False


def test_all_black_returns_bool():
    assert isinstance(ppm_all_black(RED), bool)
