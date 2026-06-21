"""Tests for XCF Sprint 67 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_WIDTH_HE-001   (Xcf Width Height Sum)
  GAP-XCF-FOSS-XCF_CANVAS_D-001   (Xcf Canvas Diagonal)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_width_height_sum, xcf_canvas_diagonal

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfWidthHeightSum:
    def test_return_type(self):
        assert isinstance(xcf_width_height_sum(_RED), int)

    def test_exact_2_for_1x1_red(self):
        assert xcf_width_height_sum(_RED) == 2

    def test_exact_2_for_1x1_blue(self):
        assert xcf_width_height_sum(_BLUE) == 2

    def test_exact_4_for_2x2_gray(self):
        assert xcf_width_height_sum(_GRAY) == 4

    def test_positive(self):
        assert xcf_width_height_sum(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_width_height_sum(_RED) == xcf_width_height_sum(_RED)


class TestXcfCanvasDiagonal:
    def test_return_type(self):
        assert isinstance(xcf_canvas_diagonal(_RED), (int, float))

    def test_approx_1_414_for_1x1_red(self):
        assert xcf_canvas_diagonal(_RED) == pytest.approx(1.4142, rel=1e-3)

    def test_approx_1_414_for_1x1_blue(self):
        assert xcf_canvas_diagonal(_BLUE) == pytest.approx(1.4142, rel=1e-3)

    def test_approx_2_828_for_2x2_gray(self):
        assert xcf_canvas_diagonal(_GRAY) == pytest.approx(2.8284, rel=1e-3)

    def test_positive(self):
        assert xcf_canvas_diagonal(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_diagonal(_RED) == xcf_canvas_diagonal(_RED)
