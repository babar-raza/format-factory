"""Tests for XCF gap closure batch 6 (Sprint 40).

Closes:
  GAP-XCF-FOSS-XCF_BYTES_PE-001   (Xcf Bytes Per Pixel)
  GAP-XCF-FOSS-XCF_IS_HIGH_-001   (Xcf Is High Resolution)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_bytes_per_pixel, xcf_is_high_res

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfBytesPerPixel:
    def test_return_type(self):
        assert isinstance(xcf_bytes_per_pixel(_1X1_RED), float)

    def test_exact_177_for_1x1_red(self):
        assert xcf_bytes_per_pixel(_1X1_RED) == 177.0

    def test_exact_178_for_1x1_blue(self):
        assert xcf_bytes_per_pixel(_1X1_BLUE) == 178.0

    def test_exact_44_5_for_2x2_gray(self):
        # 4 pixels, overhead spread -> 44.5
        assert xcf_bytes_per_pixel(_2X2_GRAY) == 44.5

    def test_positive(self):
        assert xcf_bytes_per_pixel(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_bytes_per_pixel(_1X1_RED) == xcf_bytes_per_pixel(_1X1_RED)


class TestXcfIsHighRes:
    def test_return_type(self):
        assert isinstance(xcf_is_high_res(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        # 1x1 pixel is not high resolution
        assert xcf_is_high_res(_1X1_RED) is False

    def test_false_for_1x1_blue(self):
        assert xcf_is_high_res(_1X1_BLUE) is False

    def test_false_for_2x2_gray(self):
        # 2x2 pixel is not high resolution
        assert xcf_is_high_res(_2X2_GRAY) is False

    def test_consistent_across_calls(self):
        assert xcf_is_high_res(_1X1_RED) == xcf_is_high_res(_1X1_RED)
