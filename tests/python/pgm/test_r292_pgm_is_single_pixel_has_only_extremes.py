"""Tests for pgm_is_single_pixel and pgm_has_only_extremes (Sprint 82, R292)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_is_single_pixel, pgm_has_only_extremes

PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


@pytest.fixture
def white1():
    return PGM / "1x1-white.pgm"


@pytest.fixture
def gradient():
    return PGM / "2x2-gradient.pgm"


@pytest.fixture
def ramp():
    return PGM / "3x1-ramp.pgm"


def test_is_single_pixel_1x1_true(white1):
    assert pgm_is_single_pixel(white1) is True


def test_is_single_pixel_gradient_false(gradient):
    assert pgm_is_single_pixel(gradient) is False


def test_is_single_pixel_ramp_false(ramp):
    assert pgm_is_single_pixel(ramp) is False


def test_is_single_pixel_returns_bool(white1):
    assert isinstance(pgm_is_single_pixel(white1), bool)


def test_has_only_extremes_1x1_true(white1):
    assert pgm_has_only_extremes(white1) is True


def test_has_only_extremes_gradient_false(gradient):
    assert pgm_has_only_extremes(gradient) is False


def test_has_only_extremes_ramp_false(ramp):
    assert pgm_has_only_extremes(ramp) is False


def test_has_only_extremes_returns_bool(gradient):
    assert isinstance(pgm_has_only_extremes(gradient), bool)


def test_single_pixel_consistent_with_total_count(white1):
    from pgm.pgm_parser import pgm_total_pixel_count
    assert pgm_is_single_pixel(white1) == (pgm_total_pixel_count(white1) == 1)


def test_has_only_extremes_single_pixel_white_true(white1):
    # 1x1-white has only 255 which equals maxval, so only extremes
    assert pgm_has_only_extremes(white1) is True
