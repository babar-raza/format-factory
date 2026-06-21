"""Tests for qoi_avg_luminance and qoi_pixels_per_row (Sprint 109, R319)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_avg_luminance, qoi_pixels_per_row

QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


def test_avg_lum_red():
    assert abs(qoi_avg_luminance(QOI / "1x1-red.qoi") - 76.245) < 0.01


def test_avg_lum_black():
    assert abs(qoi_avg_luminance(QOI / "2x2-black.qoi") - 0.0) < 0.01


def test_avg_lum_gradient():
    assert abs(qoi_avg_luminance(QOI / "4x1-gradient.qoi") - 127.5) < 0.01


def test_avg_lum_returns_float():
    assert isinstance(qoi_avg_luminance(QOI / "1x1-red.qoi"), float)


def test_avg_lum_nonnegative():
    assert qoi_avg_luminance(QOI / "1x1-red.qoi") >= 0.0


def test_ppr_1x1():
    assert abs(qoi_pixels_per_row(QOI / "1x1-red.qoi") - 1.0) < 0.01


def test_ppr_2x2():
    assert abs(qoi_pixels_per_row(QOI / "2x2-black.qoi") - 2.0) < 0.01


def test_ppr_4x1():
    assert abs(qoi_pixels_per_row(QOI / "4x1-gradient.qoi") - 4.0) < 0.01


def test_ppr_returns_float():
    assert isinstance(qoi_pixels_per_row(QOI / "1x1-red.qoi"), float)


def test_ppr_positive():
    assert qoi_pixels_per_row(QOI / "2x2-black.qoi") > 0.0
