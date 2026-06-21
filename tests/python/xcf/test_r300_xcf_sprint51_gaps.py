"""Tests for XCF Sprint 51 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_LAYER_WI-001  (Xcf Layer Width Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_layer_width_sum

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_1X1 = str(_DIR / "1x1-red-rgb.xcf")
_BLUE_1X1 = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_DIR / "2x2-gray.xcf")


class TestXcfLayerWidthSum:
    def test_return_type(self):
        assert isinstance(xcf_layer_width_sum(_RED_1X1), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_layer_width_sum(_RED_1X1) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_layer_width_sum(_BLUE_1X1) == 1

    def test_exact_2_for_2x2_gray(self):
        assert xcf_layer_width_sum(_GRAY_2X2) == 2

    def test_positive(self):
        assert xcf_layer_width_sum(_RED_1X1) > 0

    def test_consistent_across_calls(self):
        assert xcf_layer_width_sum(_RED_1X1) == xcf_layer_width_sum(_RED_1X1)
