"""Tests for XCF Sprint 41 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_MEGAPIXE-001  (Xcf Megapixels)
  GAP-XCF-FOSS-XCF_WIDTH_TO-001  (Xcf Width To Height Ratio)
  GAP-XCF-FOSS-XCF_CANVAS_A-002  (Xcf Canvas Area)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_area, xcf_megapixels, xcf_width_to_height_ratio

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfMegapixels:
    def test_return_type(self):
        assert isinstance(xcf_megapixels(_1X1_RED), float)

    def test_exact_1e6_for_1x1_red(self):
        assert xcf_megapixels(_1X1_RED) == 1e-6

    def test_positive(self):
        assert xcf_megapixels(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_megapixels(_1X1_RED) == xcf_megapixels(_1X1_RED)


class TestXcfWidthToHeightRatio:
    def test_return_type(self):
        assert isinstance(xcf_width_to_height_ratio(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        assert xcf_width_to_height_ratio(_1X1_RED) == 1.0

    def test_exact_1_0_for_1x1_blue(self):
        assert xcf_width_to_height_ratio(_1X1_BLUE) == 1.0

    def test_exact_1_0_for_2x2_gray(self):
        assert xcf_width_to_height_ratio(_2X2_GRAY) == 1.0

    def test_positive(self):
        assert xcf_width_to_height_ratio(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_width_to_height_ratio(_1X1_RED) == xcf_width_to_height_ratio(_1X1_RED)


class TestXcfCanvasArea:
    def test_return_type(self):
        assert isinstance(xcf_canvas_area(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_canvas_area(_1X1_RED) == 1

    def test_exact_4_for_2x2_gray(self):
        assert xcf_canvas_area(_2X2_GRAY) == 4

    def test_positive(self):
        assert xcf_canvas_area(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_area(_1X1_RED) == xcf_canvas_area(_1X1_RED)
