"""Tests for QOI Sprint 56 batch 2 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_PIXEL_UN-001  (Qoi Pixel Uniformity)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_pixel_uniformity

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiPixelUniformity:
    def test_return_type(self):
        assert isinstance(qoi_pixel_uniformity(_RED), (int, float))

    def test_exact_1_for_red(self):
        assert qoi_pixel_uniformity(_RED) == 1.0

    def test_exact_1_for_black(self):
        assert qoi_pixel_uniformity(_BLACK) == 1.0

    def test_exact_0_25_for_gradient(self):
        assert qoi_pixel_uniformity(_GRADIENT) == 0.25

    def test_in_range_0_to_1(self):
        assert 0.0 <= qoi_pixel_uniformity(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_pixel_uniformity(_RED) == qoi_pixel_uniformity(_RED)
