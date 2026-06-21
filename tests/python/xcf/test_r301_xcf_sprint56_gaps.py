"""Tests for XCF Sprint 56 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_TOTAL_CA-001  (Xcf Total Canvas Pixels)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_total_canvas_pixels

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_1X1 = str(_DIR / "1x1-red-rgb.xcf")
_BLUE_1X1 = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_DIR / "2x2-gray.xcf")


class TestXcfTotalCanvasPixels:
    def test_return_type(self):
        assert isinstance(xcf_total_canvas_pixels(_RED_1X1), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_total_canvas_pixels(_RED_1X1) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_total_canvas_pixels(_BLUE_1X1) == 1

    def test_exact_4_for_2x2_gray(self):
        assert xcf_total_canvas_pixels(_GRAY_2X2) == 4

    def test_positive(self):
        assert xcf_total_canvas_pixels(_RED_1X1) > 0

    def test_consistent_across_calls(self):
        assert xcf_total_canvas_pixels(_RED_1X1) == xcf_total_canvas_pixels(_RED_1X1)
