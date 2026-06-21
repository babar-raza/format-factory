"""Tests for XCF Sprint 72 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_CANVAS_H-001   (Xcf Canvas Half Perimeter)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_half_perimeter

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfCanvasHalfPerimeter:
    def test_return_type(self):
        assert isinstance(xcf_canvas_half_perimeter(_RED), int)

    def test_exact_2_for_1x1_red(self):
        assert xcf_canvas_half_perimeter(_RED) == 2

    def test_exact_2_for_1x1_blue(self):
        assert xcf_canvas_half_perimeter(_BLUE) == 2

    def test_exact_4_for_2x2_gray(self):
        assert xcf_canvas_half_perimeter(_GRAY) == 4

    def test_positive(self):
        assert xcf_canvas_half_perimeter(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_half_perimeter(_RED) == xcf_canvas_half_perimeter(_RED)
