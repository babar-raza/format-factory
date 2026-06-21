"""Tests for xcf_canvas_aspect_ratio (Sprint 40 batch 2).

Closes:
  GAP-XCF-FOSS-XCF_CANVAS_A-001  (Xcf Canvas Aspect Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_canvas_aspect_ratio

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RED = str(_DIR / "1x1-red-rgb.xcf")
_1X1_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_2X2_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfCanvasAspectRatio:
    def test_return_type(self):
        assert isinstance(xcf_canvas_aspect_ratio(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        # 1x1 image -> aspect ratio = width/height = 1.0
        assert xcf_canvas_aspect_ratio(_1X1_RED) == 1.0

    def test_exact_1_0_for_1x1_blue(self):
        assert xcf_canvas_aspect_ratio(_1X1_BLUE) == 1.0

    def test_exact_1_0_for_2x2_gray(self):
        # 2x2 square image -> aspect ratio = 1.0
        assert xcf_canvas_aspect_ratio(_2X2_GRAY) == 1.0

    def test_positive(self):
        assert xcf_canvas_aspect_ratio(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_canvas_aspect_ratio(_1X1_RED) == xcf_canvas_aspect_ratio(_1X1_RED)
