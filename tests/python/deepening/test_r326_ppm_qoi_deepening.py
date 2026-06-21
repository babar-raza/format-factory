"""Tests for ppm_avg_blue_channel, ppm_max_channel_spread,
qoi_blue_dominant_count, qoi_max_channel_spread (Sprint 116, R326).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_avg_blue_channel, ppm_max_channel_spread
from src.python.qoi.qoi_parser import qoi_blue_dominant_count, qoi_max_channel_spread

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


def test_ppm_avg_blue_red():
    assert abs(ppm_avg_blue_channel(PPM / "1x1-red.ppm") - 0.0) < 0.01


def test_ppm_avg_blue_rgbw():
    assert abs(ppm_avg_blue_channel(PPM / "2x2-rgbw.ppm") - 127.5) < 0.1


def test_ppm_avg_blue_gradient():
    assert abs(ppm_avg_blue_channel(PPM / "3x1-gradient.ppm") - 127.67) < 0.1


def test_ppm_avg_blue_returns_float():
    assert isinstance(ppm_avg_blue_channel(PPM / "1x1-red.ppm"), float)


def test_ppm_avg_blue_nonnegative():
    assert ppm_avg_blue_channel(PPM / "1x1-red.ppm") >= 0.0


def test_ppm_spread_red():
    assert ppm_max_channel_spread(PPM / "1x1-red.ppm") == 255


def test_ppm_spread_rgbw():
    assert ppm_max_channel_spread(PPM / "2x2-rgbw.ppm") == 255


def test_ppm_spread_gradient():
    assert ppm_max_channel_spread(PPM / "3x1-gradient.ppm") == 0


def test_ppm_spread_returns_int():
    assert isinstance(ppm_max_channel_spread(PPM / "1x1-red.ppm"), int)


def test_ppm_spread_nonnegative():
    assert ppm_max_channel_spread(PPM / "1x1-red.ppm") >= 0


def test_qoi_blue_dom_red():
    assert qoi_blue_dominant_count(QOI / "1x1-red.qoi") == 0


def test_qoi_blue_dom_black():
    assert qoi_blue_dominant_count(QOI / "2x2-black.qoi") == 0


def test_qoi_blue_dom_gradient():
    assert qoi_blue_dominant_count(QOI / "4x1-gradient.qoi") == 0


def test_qoi_blue_dom_returns_int():
    assert isinstance(qoi_blue_dominant_count(QOI / "1x1-red.qoi"), int)


def test_qoi_blue_dom_nonnegative():
    assert qoi_blue_dominant_count(QOI / "1x1-red.qoi") >= 0


def test_qoi_spread_red():
    assert qoi_max_channel_spread(QOI / "1x1-red.qoi") == 255


def test_qoi_spread_black():
    assert qoi_max_channel_spread(QOI / "2x2-black.qoi") == 0


def test_qoi_spread_gradient():
    assert qoi_max_channel_spread(QOI / "4x1-gradient.qoi") == 0


def test_qoi_spread_returns_int():
    assert isinstance(qoi_max_channel_spread(QOI / "1x1-red.qoi"), int)


def test_qoi_spread_nonnegative():
    assert qoi_max_channel_spread(QOI / "1x1-red.qoi") >= 0
