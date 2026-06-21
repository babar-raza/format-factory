"""Tests for qoi_width and qoi_height (Sprint 95, R305)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_width, qoi_height

QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


def test_width_1x1():
    assert qoi_width(QOI / "1x1-red.qoi") == 1


def test_width_2x2():
    assert qoi_width(QOI / "2x2-black.qoi") == 2


def test_width_4x1():
    assert qoi_width(QOI / "4x1-gradient.qoi") == 4


def test_width_returns_int():
    assert isinstance(qoi_width(QOI / "1x1-red.qoi"), int)


def test_width_positive():
    assert qoi_width(QOI / "2x2-black.qoi") > 0


def test_height_1x1():
    assert qoi_height(QOI / "1x1-red.qoi") == 1


def test_height_2x2():
    assert qoi_height(QOI / "2x2-black.qoi") == 2


def test_height_4x1():
    assert qoi_height(QOI / "4x1-gradient.qoi") == 1


def test_height_returns_int():
    assert isinstance(qoi_height(QOI / "1x1-red.qoi"), int)


def test_height_positive():
    assert qoi_height(QOI / "2x2-black.qoi") > 0
