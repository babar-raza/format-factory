"""Tests for xcf_pixel_per_layer_avg (Sprint 40 batch 3).

Closes:
  GAP-XCF-FOSS-XCF_PIXEL_PE-001  (Xcf Pixel Per Layer)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_pixel_per_layer_avg

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfPixelPerLayerAvg:
    def test_return_type(self):
        assert isinstance(xcf_pixel_per_layer_avg(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        # 1x1 image, 1 layer -> avg pixels per layer = 1.0
        assert xcf_pixel_per_layer_avg(_1X1_RED) == 1.0

    def test_exact_1_0_for_1x1_blue(self):
        assert xcf_pixel_per_layer_avg(_1X1_BLUE) == 1.0

    def test_exact_4_0_for_2x2_gray(self):
        # 2x2 image, 1 layer -> avg pixels per layer = 4.0
        assert xcf_pixel_per_layer_avg(_2X2_GRAY) == 4.0

    def test_positive(self):
        assert xcf_pixel_per_layer_avg(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_pixel_per_layer_avg(_1X1_RED) == xcf_pixel_per_layer_avg(_1X1_RED)
