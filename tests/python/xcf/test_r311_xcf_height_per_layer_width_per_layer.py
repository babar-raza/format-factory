"""Tests for xcf_height_per_layer and xcf_width_per_layer (Sprint 101, R311)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_height_per_layer, xcf_width_per_layer

XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"


def test_height_per_layer_red():
    assert abs(xcf_height_per_layer(XCF / "1x1-red-rgb.xcf") - 1.0) < 0.001


def test_height_per_layer_blue():
    assert abs(xcf_height_per_layer(XCF / "1x1-rgba-blue.xcf") - 1.0) < 0.001


def test_height_per_layer_gray():
    assert abs(xcf_height_per_layer(XCF / "2x2-gray.xcf") - 2.0) < 0.001


def test_height_per_layer_returns_float():
    assert isinstance(xcf_height_per_layer(XCF / "1x1-red-rgb.xcf"), float)


def test_height_per_layer_positive():
    assert xcf_height_per_layer(XCF / "2x2-gray.xcf") > 0.0


def test_width_per_layer_red():
    assert abs(xcf_width_per_layer(XCF / "1x1-red-rgb.xcf") - 1.0) < 0.001


def test_width_per_layer_blue():
    assert abs(xcf_width_per_layer(XCF / "1x1-rgba-blue.xcf") - 1.0) < 0.001


def test_width_per_layer_gray():
    assert abs(xcf_width_per_layer(XCF / "2x2-gray.xcf") - 2.0) < 0.001


def test_width_per_layer_returns_float():
    assert isinstance(xcf_width_per_layer(XCF / "1x1-red-rgb.xcf"), float)


def test_width_per_layer_positive():
    assert xcf_width_per_layer(XCF / "2x2-gray.xcf") > 0.0
