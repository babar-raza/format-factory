"""Tests for PGM image analytics in pgm_image_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_image_analytics import (
    pgm_width,
    pgm_height,
    pgm_maxval,
    pgm_magic,
    pgm_is_single_pixel,
    pgm_is_full_range,
)

SAMPLES = Path("samples/by-format/pgm/valid")
P1X1 = SAMPLES / "1x1-white.pgm"       # 1x1, maxval=255, pixel=255, magic=P2
P2X2 = SAMPLES / "2x2-gradient.pgm"    # 2x2, maxval=255, pixels=[0,85,170,255]
P3X1 = SAMPLES / "3x1-ramp.pgm"        # 3x1, maxval=255, pixels=[0,128,255]


# --- pgm_width ---

def test_width_1x1():
    assert pgm_width(P1X1) == 1


def test_width_2x2():
    assert pgm_width(P2X2) == 2


def test_width_3x1():
    assert pgm_width(P3X1) == 3


def test_width_returns_int():
    assert isinstance(pgm_width(P1X1), int)


# --- pgm_height ---

def test_height_1x1():
    assert pgm_height(P1X1) == 1


def test_height_2x2():
    assert pgm_height(P2X2) == 2


def test_height_3x1():
    assert pgm_height(P3X1) == 1


def test_height_returns_int():
    assert isinstance(pgm_height(P1X1), int)


# --- pgm_maxval ---

def test_maxval_1x1():
    assert pgm_maxval(P1X1) == 255


def test_maxval_2x2():
    assert pgm_maxval(P2X2) == 255


def test_maxval_returns_int():
    assert isinstance(pgm_maxval(P1X1), int)


# --- pgm_magic ---

def test_magic_1x1():
    assert pgm_magic(P1X1) == "P2"


def test_magic_2x2():
    assert pgm_magic(P2X2) == "P2"


def test_magic_returns_str():
    assert isinstance(pgm_magic(P1X1), str)


# --- pgm_is_single_pixel ---

def test_is_single_pixel_1x1():
    assert pgm_is_single_pixel(P1X1) is True


def test_is_single_pixel_2x2():
    assert pgm_is_single_pixel(P2X2) is False


def test_is_single_pixel_3x1():
    assert pgm_is_single_pixel(P3X1) is False


def test_is_single_pixel_returns_bool():
    assert isinstance(pgm_is_single_pixel(P1X1), bool)


# --- pgm_is_full_range ---

def test_is_full_range_1x1():
    # 1x1-white.pgm has only pixel=255, so min=255 != 0 → not full range
    assert pgm_is_full_range(P1X1) is False


def test_is_full_range_2x2():
    # 2x2-gradient has pixels [0,85,170,255] → min=0, max=255 → full range
    assert pgm_is_full_range(P2X2) is True


def test_is_full_range_3x1():
    # 3x1-ramp has pixels [0,128,255] → min=0, max=255 → full range
    assert pgm_is_full_range(P3X1) is True


def test_is_full_range_returns_bool():
    assert isinstance(pgm_is_full_range(P1X1), bool)
