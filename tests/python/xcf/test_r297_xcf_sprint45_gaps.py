"""Tests for XCF Sprint 45 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_IS_SQUAR-001  (Xcf Is Square Canvas)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_is_square_canvas

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_1X1 = str(_DIR / "1x1-red-rgb.xcf")
_BLUE_1X1 = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_DIR / "2x2-gray.xcf")


class TestXcfIsSquareCanvas:
    def test_return_type(self):
        assert isinstance(xcf_is_square_canvas(_RED_1X1), bool)

    def test_true_for_1x1_red(self):
        assert xcf_is_square_canvas(_RED_1X1) is True

    def test_true_for_1x1_blue(self):
        assert xcf_is_square_canvas(_BLUE_1X1) is True

    def test_true_for_2x2_gray(self):
        assert xcf_is_square_canvas(_GRAY_2X2) is True

    def test_consistent_across_calls(self):
        assert xcf_is_square_canvas(_RED_1X1) == xcf_is_square_canvas(_RED_1X1)
