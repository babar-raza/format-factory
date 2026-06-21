"""Tests for ppm_width and ppm_height (Sprint 91, R301)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_width, ppm_height

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


@pytest.fixture
def red1x1():
    return PPM / "1x1-red.ppm"


@pytest.fixture
def rgbw2x2():
    return PPM / "2x2-rgbw.ppm"


@pytest.fixture
def grad3x1():
    return PPM / "3x1-gradient.ppm"


def test_width_1x1(red1x1):
    assert ppm_width(red1x1) == 1


def test_width_2x2(rgbw2x2):
    assert ppm_width(rgbw2x2) == 2


def test_width_3x1(grad3x1):
    assert ppm_width(grad3x1) == 3


def test_width_returns_int(red1x1):
    assert isinstance(ppm_width(red1x1), int)


def test_width_positive(rgbw2x2):
    assert ppm_width(rgbw2x2) > 0


def test_height_1x1(red1x1):
    assert ppm_height(red1x1) == 1


def test_height_2x2(rgbw2x2):
    assert ppm_height(rgbw2x2) == 2


def test_height_3x1(grad3x1):
    assert ppm_height(grad3x1) == 1


def test_height_returns_int(red1x1):
    assert isinstance(ppm_height(red1x1), int)


def test_height_positive(rgbw2x2):
    assert ppm_height(rgbw2x2) > 0
