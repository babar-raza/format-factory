"""Tests for PPM stats extension functions in ppm_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import parse_ppm
from src.python.ppm.ppm_stats import (
    ppm_is_square,
    ppm_is_landscape,
    ppm_is_portrait,
    ppm_is_ok,
    ppm_is_ascii_ppm,
    ppm_aspect_ratio_from_doc,
)

SAMPLES = Path("samples/by-format/ppm/valid")
RED_1X1  = SAMPLES / "1x1-red.ppm"       # w=1 h=1 maxval=255 magic=P3
RGBW_2X2 = SAMPLES / "2x2-rgbw.ppm"     # w=2 h=2 maxval=255 magic=P3
GRAD_3X1 = SAMPLES / "3x1-gradient.ppm"  # w=3 h=1 maxval=255 magic=P3

def _doc(path):
    return parse_ppm(path)


# ppm_is_square
def test_is_square_1x1():
    assert ppm_is_square(_doc(RED_1X1)) is True

def test_is_square_2x2():
    assert ppm_is_square(_doc(RGBW_2X2)) is True

def test_is_square_3x1():
    assert ppm_is_square(_doc(GRAD_3X1)) is False

def test_is_square_returns_bool():
    assert isinstance(ppm_is_square(_doc(RED_1X1)), bool)


# ppm_is_landscape
def test_is_landscape_3x1():
    # w=3 > h=1 → landscape
    assert ppm_is_landscape(_doc(GRAD_3X1)) is True

def test_is_landscape_1x1():
    assert ppm_is_landscape(_doc(RED_1X1)) is False

def test_is_landscape_returns_bool():
    assert isinstance(ppm_is_landscape(_doc(RED_1X1)), bool)


# ppm_is_portrait
def test_is_portrait_1x1():
    assert ppm_is_portrait(_doc(RED_1X1)) is False

def test_is_portrait_3x1():
    assert ppm_is_portrait(_doc(GRAD_3X1)) is False

def test_is_portrait_returns_bool():
    assert isinstance(ppm_is_portrait(_doc(RED_1X1)), bool)


# ppm_is_ok
def test_is_ok_1x1():
    assert ppm_is_ok(_doc(RED_1X1)) is True

def test_is_ok_returns_bool():
    assert isinstance(ppm_is_ok(_doc(RED_1X1)), bool)


# ppm_is_ascii_ppm
def test_is_ascii_ppm_1x1():
    assert ppm_is_ascii_ppm(_doc(RED_1X1)) is True

def test_is_ascii_ppm_2x2():
    assert ppm_is_ascii_ppm(_doc(RGBW_2X2)) is True

def test_is_ascii_ppm_returns_bool():
    assert isinstance(ppm_is_ascii_ppm(_doc(RED_1X1)), bool)


# ppm_aspect_ratio_from_doc
def test_aspect_ratio_1x1():
    assert ppm_aspect_ratio_from_doc(_doc(RED_1X1)) == pytest.approx(1.0)

def test_aspect_ratio_3x1():
    assert ppm_aspect_ratio_from_doc(_doc(GRAD_3X1)) == pytest.approx(3.0)

def test_aspect_ratio_returns_float():
    assert isinstance(ppm_aspect_ratio_from_doc(_doc(RED_1X1)), float)
