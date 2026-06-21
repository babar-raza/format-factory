"""Tests for XCF Sprint 41 batch 2 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_CANVAS_P-001  (Xcf Canvas Perimeter)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_perimeter

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfCanvasPerimeter:
    def test_return_type(self):
        assert isinstance(xcf_canvas_perimeter(_1X1_RED), int)

    def test_exact_4_for_1x1_red(self):
        assert xcf_canvas_perimeter(_1X1_RED) == 4

    def test_exact_4_for_1x1_blue(self):
        assert xcf_canvas_perimeter(_1X1_BLUE) == 4

    def test_exact_8_for_2x2_gray(self):
        assert xcf_canvas_perimeter(_2X2_GRAY) == 8

    def test_positive(self):
        assert xcf_canvas_perimeter(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_perimeter(_1X1_RED) == xcf_canvas_perimeter(_1X1_RED)
