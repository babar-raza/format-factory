"""Tests for QOI Sprint 46 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_PIXEL_BR-001  (Qoi Pixel Brightness Range)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_pixel_brightness_range

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiPixelBrightnessRange:
    def test_return_type(self):
        assert isinstance(qoi_pixel_brightness_range(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert qoi_pixel_brightness_range(_RED) == 0

    def test_zero_for_2x2_black(self):
        assert qoi_pixel_brightness_range(_BLACK) == 0

    def test_exact_255_for_gradient(self):
        assert qoi_pixel_brightness_range(_GRADIENT) == 255

    def test_nonnegative(self):
        assert qoi_pixel_brightness_range(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_pixel_brightness_range(_RED) == qoi_pixel_brightness_range(_RED)
