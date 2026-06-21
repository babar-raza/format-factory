"""Tests for qoi_total_red_sum and qoi_nonblack_pixel_ratio (Sprint 100, R310)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_total_red_sum, qoi_nonblack_pixel_ratio

QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


def test_total_red_sum_red():
    assert qoi_total_red_sum(QOI / "1x1-red.qoi") == 255


def test_total_red_sum_black():
    assert qoi_total_red_sum(QOI / "2x2-black.qoi") == 0


def test_total_red_sum_gradient():
    assert qoi_total_red_sum(QOI / "4x1-gradient.qoi") == 510


def test_total_red_sum_returns_int():
    assert isinstance(qoi_total_red_sum(QOI / "1x1-red.qoi"), int)


def test_total_red_sum_nonnegative():
    assert qoi_total_red_sum(QOI / "4x1-gradient.qoi") >= 0


def test_nonblack_ratio_red():
    assert abs(qoi_nonblack_pixel_ratio(QOI / "1x1-red.qoi") - 1.0) < 0.001


def test_nonblack_ratio_black():
    assert abs(qoi_nonblack_pixel_ratio(QOI / "2x2-black.qoi") - 0.0) < 0.001


def test_nonblack_ratio_gradient():
    assert abs(qoi_nonblack_pixel_ratio(QOI / "4x1-gradient.qoi") - 0.75) < 0.001


def test_nonblack_ratio_returns_float():
    assert isinstance(qoi_nonblack_pixel_ratio(QOI / "1x1-red.qoi"), float)


def test_nonblack_ratio_nonnegative():
    assert qoi_nonblack_pixel_ratio(QOI / "2x2-black.qoi") >= 0.0
