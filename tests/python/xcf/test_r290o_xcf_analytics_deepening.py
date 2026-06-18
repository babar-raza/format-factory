"""Tests for XCF analytics deepening (R290O): canvas_fill_ratio, is_tiny."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_canvas_fill_ratio, xcf_is_tiny

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


def test_canvas_fill_ratio_returns_float():
    result = xcf_canvas_fill_ratio(SAMPLES / "1x1-red-rgb.xcf")
    assert isinstance(result, float)
    assert result >= 0.0


def test_canvas_fill_ratio_gray():
    result = xcf_canvas_fill_ratio(SAMPLES / "2x2-gray.xcf")
    assert isinstance(result, float)


def test_is_tiny_returns_bool():
    result = xcf_is_tiny(SAMPLES / "1x1-red-rgb.xcf")
    assert isinstance(result, bool)
    assert result is True  # 1x1 = 1 pixel < 100


def test_is_tiny_2x2():
    result = xcf_is_tiny(SAMPLES / "2x2-gray.xcf")
    assert isinstance(result, bool)
    assert result is True  # 2x2 = 4 pixels < 100


def test_canvas_fill_ratio_rgba():
    result = xcf_canvas_fill_ratio(SAMPLES / "1x1-rgba-blue.xcf")
    assert isinstance(result, float)


def test_is_tiny_rgba():
    result = xcf_is_tiny(SAMPLES / "1x1-rgba-blue.xcf")
    assert result is True
