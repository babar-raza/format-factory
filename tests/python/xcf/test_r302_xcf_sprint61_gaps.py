"""Tests for XCF Sprint 61 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_HEIGHT_S-001   (Xcf Height Squared)
  GAP-XCF-FOSS-XCF_WIDTH_SQ-001   (Xcf Width Squared)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_height_squared, xcf_width_squared

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfHeightSquared:
    def test_return_type(self):
        assert isinstance(xcf_height_squared(_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_height_squared(_RED) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_height_squared(_BLUE) == 1

    def test_exact_4_for_2x2(self):
        assert xcf_height_squared(_GRAY) == 4

    def test_positive(self):
        assert xcf_height_squared(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_height_squared(_RED) == xcf_height_squared(_RED)


class TestXcfWidthSquared:
    def test_return_type(self):
        assert isinstance(xcf_width_squared(_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_width_squared(_RED) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_width_squared(_BLUE) == 1

    def test_exact_4_for_2x2(self):
        assert xcf_width_squared(_GRAY) == 4

    def test_positive(self):
        assert xcf_width_squared(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_width_squared(_RED) == xcf_width_squared(_RED)
