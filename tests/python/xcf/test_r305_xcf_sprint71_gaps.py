"""Tests for XCF Sprint 71 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_CANVAS_F-001   (Xcf Canvas Fill Ratio)
  GAP-XCF-FOSS-XCF_IS_TINY-001    (Xcf Is Tiny)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_fill_ratio, xcf_is_tiny

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfCanvasFillRatio:
    def test_return_type(self):
        assert isinstance(xcf_canvas_fill_ratio(_RED), (int, float))

    def test_exact_1_0_for_1x1_red(self):
        assert xcf_canvas_fill_ratio(_RED) == 1.0

    def test_exact_1_0_for_1x1_blue(self):
        assert xcf_canvas_fill_ratio(_BLUE) == 1.0

    def test_exact_0_25_for_2x2_gray(self):
        assert xcf_canvas_fill_ratio(_GRAY) == 0.25

    def test_between_0_and_1(self):
        assert 0.0 <= xcf_canvas_fill_ratio(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert xcf_canvas_fill_ratio(_RED) == xcf_canvas_fill_ratio(_RED)


class TestXcfIsTiny:
    def test_return_type(self):
        assert isinstance(xcf_is_tiny(_RED), bool)

    def test_true_for_1x1_red(self):
        assert xcf_is_tiny(_RED) is True

    def test_true_for_1x1_blue(self):
        assert xcf_is_tiny(_BLUE) is True

    def test_true_for_2x2_gray(self):
        assert xcf_is_tiny(_GRAY) is True

    def test_is_boolean(self):
        assert xcf_is_tiny(_RED) in (True, False)

    def test_consistent_across_calls(self):
        assert xcf_is_tiny(_RED) == xcf_is_tiny(_RED)
