"""Tests for qoi_has_warm_pixels and qoi_is_monochromatic (Sprint 78, R288)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import qoi_has_warm_pixels, qoi_is_monochromatic

QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


@pytest.fixture
def red():
    return QOI / "1x1-red.qoi"


@pytest.fixture
def black():
    return QOI / "2x2-black.qoi"


@pytest.fixture
def gradient():
    return QOI / "4x1-gradient.qoi"


def test_has_warm_pixels_red_true(red):
    assert qoi_has_warm_pixels(red) is True


def test_has_warm_pixels_black_false(black):
    assert qoi_has_warm_pixels(black) is False


def test_has_warm_pixels_gradient_false(gradient):
    assert qoi_has_warm_pixels(gradient) is False


def test_has_warm_pixels_returns_bool(red):
    assert isinstance(qoi_has_warm_pixels(red), bool)


def test_is_monochromatic_red_true(red):
    assert qoi_is_monochromatic(red) is True


def test_is_monochromatic_black_true(black):
    assert qoi_is_monochromatic(black) is True


def test_is_monochromatic_gradient_false(gradient):
    assert qoi_is_monochromatic(gradient) is False


def test_is_monochromatic_returns_bool(gradient):
    assert isinstance(qoi_is_monochromatic(gradient), bool)


def test_warm_and_mono_consistent_red(red):
    # red pixel: has warm pixels and is monochromatic (only one color)
    assert qoi_has_warm_pixels(red) and qoi_is_monochromatic(red)


def test_not_mono_implies_multiple_colors(gradient):
    from qoi.qoi_parser import qoi_color_count
    if not qoi_is_monochromatic(gradient):
        assert qoi_color_count(gradient) > 1
