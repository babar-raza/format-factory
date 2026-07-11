"""Tests for extended PBM bitmap analytics (width, height, magic, is_ascii_format, is_single_pixel)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.bitmap_image import (
    pbm_width,
    pbm_height,
    pbm_magic,
    pbm_is_ascii_format,
    pbm_is_single_pixel,
)

SAMPLES = Path("samples/by-format/pbm/valid")
P1X1 = SAMPLES / "1x1-black.pbm"      # 1x1, magic P1
P2X2 = SAMPLES / "2x2-checker.pbm"    # 2x2, magic P1
P3X2 = SAMPLES / "3x2-pattern.pbm"    # 3x2, magic P1


# --- pbm_width ---

def test_width_1x1():
    assert pbm_width(P1X1) == 1


def test_width_2x2():
    assert pbm_width(P2X2) == 2


def test_width_3x2():
    assert pbm_width(P3X2) == 3


def test_width_returns_int():
    assert isinstance(pbm_width(P1X1), int)


# --- pbm_height ---

def test_height_1x1():
    assert pbm_height(P1X1) == 1


def test_height_2x2():
    assert pbm_height(P2X2) == 2


def test_height_3x2():
    assert pbm_height(P3X2) == 2


def test_height_returns_int():
    assert isinstance(pbm_height(P1X1), int)


# --- pbm_magic ---

def test_magic_1x1():
    assert pbm_magic(P1X1) == "P1"


def test_magic_2x2():
    assert pbm_magic(P2X2) == "P1"


def test_magic_returns_str():
    assert isinstance(pbm_magic(P1X1), str)


# --- pbm_is_ascii_format ---

def test_is_ascii_format_1x1():
    assert pbm_is_ascii_format(P1X1) is True


def test_is_ascii_format_2x2():
    assert pbm_is_ascii_format(P2X2) is True


def test_is_ascii_format_returns_bool():
    assert isinstance(pbm_is_ascii_format(P1X1), bool)


# --- pbm_is_single_pixel ---

def test_is_single_pixel_1x1():
    assert pbm_is_single_pixel(P1X1) is True


def test_is_single_pixel_2x2():
    assert pbm_is_single_pixel(P2X2) is False


def test_is_single_pixel_3x2():
    assert pbm_is_single_pixel(P3X2) is False


def test_is_single_pixel_returns_bool():
    assert isinstance(pbm_is_single_pixel(P1X1), bool)
