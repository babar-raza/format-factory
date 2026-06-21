"""Tests for QOI Sprint 52 batch 2 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_MAX_RED_-001   (Qoi Max Red Value)
  GAP-QOI-FOSS-QOI_GRAYSCAL-001   (Qoi Grayscale Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_max_red_value, qoi_grayscale_pixel_count

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiMaxRedValue:
    def test_return_type(self):
        assert isinstance(qoi_max_red_value(_RED), int)

    def test_exact_255_for_red(self):
        assert qoi_max_red_value(_RED) == 255

    def test_zero_for_black(self):
        assert qoi_max_red_value(_BLACK) == 0

    def test_exact_255_for_gradient(self):
        assert qoi_max_red_value(_GRADIENT) == 255

    def test_nonnegative(self):
        assert qoi_max_red_value(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_max_red_value(_RED) == qoi_max_red_value(_RED)


class TestQoiGrayscalePixelCount:
    def test_return_type(self):
        assert isinstance(qoi_grayscale_pixel_count(_RED), int)

    def test_zero_for_red(self):
        assert qoi_grayscale_pixel_count(_RED) == 0

    def test_exact_4_for_black(self):
        assert qoi_grayscale_pixel_count(_BLACK) == 4

    def test_exact_4_for_gradient(self):
        assert qoi_grayscale_pixel_count(_GRADIENT) == 4

    def test_nonnegative(self):
        assert qoi_grayscale_pixel_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_grayscale_pixel_count(_RED) == qoi_grayscale_pixel_count(_RED)
