"""Tests for pgm_width and pgm_height (Sprint 91, R301)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_width, pgm_height

PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


@pytest.fixture
def white1x1():
    return PGM / "1x1-white.pgm"


@pytest.fixture
def gradient2x2():
    return PGM / "2x2-gradient.pgm"


@pytest.fixture
def ramp3x1():
    return PGM / "3x1-ramp.pgm"


def test_width_1x1(white1x1):
    assert pgm_width(white1x1) == 1


def test_width_2x2(gradient2x2):
    assert pgm_width(gradient2x2) == 2


def test_width_3x1(ramp3x1):
    assert pgm_width(ramp3x1) == 3


def test_width_returns_int(white1x1):
    assert isinstance(pgm_width(white1x1), int)


def test_width_positive(gradient2x2):
    assert pgm_width(gradient2x2) > 0


def test_height_1x1(white1x1):
    assert pgm_height(white1x1) == 1


def test_height_2x2(gradient2x2):
    assert pgm_height(gradient2x2) == 2


def test_height_3x1(ramp3x1):
    assert pgm_height(ramp3x1) == 1


def test_height_returns_int(white1x1):
    assert isinstance(pgm_height(white1x1), int)


def test_height_positive(gradient2x2):
    assert pgm_height(gradient2x2) > 0
