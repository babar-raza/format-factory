"""Tests for XCF Sprint 46 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_HAS_SING-001  (Xcf Has Single Layer)
  GAP-XCF-FOSS-XCF_ASPECT_R-001  (Xcf Aspect Ratio String)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_has_single_layer, xcf_aspect_ratio_string

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_1X1 = str(_DIR / "1x1-red-rgb.xcf")
_BLUE_1X1 = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_DIR / "2x2-gray.xcf")


class TestXcfHasSingleLayer:
    def test_return_type(self):
        assert isinstance(xcf_has_single_layer(_RED_1X1), bool)

    def test_true_for_1x1_red(self):
        assert xcf_has_single_layer(_RED_1X1) is True

    def test_true_for_1x1_blue(self):
        assert xcf_has_single_layer(_BLUE_1X1) is True

    def test_true_for_2x2_gray(self):
        assert xcf_has_single_layer(_GRAY_2X2) is True

    def test_consistent_across_calls(self):
        assert xcf_has_single_layer(_RED_1X1) == xcf_has_single_layer(_RED_1X1)


class TestXcfAspectRatioString:
    def test_return_type(self):
        assert isinstance(xcf_aspect_ratio_string(_RED_1X1), str)

    def test_exact_1_1_for_1x1_red(self):
        assert xcf_aspect_ratio_string(_RED_1X1) == "1:1"

    def test_exact_1_1_for_1x1_blue(self):
        assert xcf_aspect_ratio_string(_BLUE_1X1) == "1:1"

    def test_exact_1_1_for_2x2_gray(self):
        assert xcf_aspect_ratio_string(_GRAY_2X2) == "1:1"

    def test_contains_colon(self):
        assert ":" in xcf_aspect_ratio_string(_RED_1X1)

    def test_consistent_across_calls(self):
        assert xcf_aspect_ratio_string(_RED_1X1) == xcf_aspect_ratio_string(_RED_1X1)
