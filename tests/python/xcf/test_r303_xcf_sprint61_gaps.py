"""Tests for XCF Sprint 61 gap closure (batch 2).

Closes:
  GAP-XCF-FOSS-XCF_IS_COLOR-001    (Xcf Is Color)
  GAP-XCF-FOSS-XCF_PIXELS_E-001    (Xcf Pixels Exceed Layers)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_is_color, xcf_pixels_exceed_layers

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfIsColor:
    def test_return_type(self):
        assert isinstance(xcf_is_color(_RED), bool)

    def test_true_for_red_rgb(self):
        assert xcf_is_color(_RED) is True

    def test_true_for_blue_rgba(self):
        assert xcf_is_color(_BLUE) is True

    def test_false_for_gray(self):
        assert xcf_is_color(_GRAY) is False

    def test_consistent_across_calls(self):
        assert xcf_is_color(_RED) == xcf_is_color(_RED)


class TestXcfPixelsExceedLayers:
    def test_return_type(self):
        assert isinstance(xcf_pixels_exceed_layers(_RED), bool)

    def test_false_for_1x1_red(self):
        assert xcf_pixels_exceed_layers(_RED) is False

    def test_false_for_1x1_blue(self):
        assert xcf_pixels_exceed_layers(_BLUE) is False

    def test_true_for_2x2_gray(self):
        assert xcf_pixels_exceed_layers(_GRAY) is True

    def test_consistent_across_calls(self):
        assert xcf_pixels_exceed_layers(_RED) == xcf_pixels_exceed_layers(_RED)
