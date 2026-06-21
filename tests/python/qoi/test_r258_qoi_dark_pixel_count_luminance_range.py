"""Tests for QOI gap closure batch 5 (Sprint 40).

Closes:
  GAP-QOI-FOSS-QOI_DARK_PIX-001   (Qoi Dark Pixel Count)
  GAP-QOI-FOSS-QOI_LUMINANC-001   (Qoi Luminance Range)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_dark_pixel_count, qoi_luminance_range

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")
_2X2_BLACK = str(_DIR / "2x2-black.qoi")
_4X1_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiDarkPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_dark_pixel_count(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        # red pixel is not below dark threshold at pixel level
        assert qoi_dark_pixel_count(_1X1_RED) == 0

    def test_exact_4_for_2x2_black(self):
        # all 4 black pixels are dark
        assert qoi_dark_pixel_count(_2X2_BLACK) == 4

    def test_positive_for_gradient(self):
        # gradient starts with black pixels
        assert qoi_dark_pixel_count(_4X1_GRAD) >= 1

    def test_nonnegative(self):
        assert qoi_dark_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_dark_pixel_count(_2X2_BLACK) == qoi_dark_pixel_count(_2X2_BLACK)


class TestQoiLuminanceRange:
    def test_return_type(self):
        assert isinstance(qoi_luminance_range(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel -> no range
        assert qoi_luminance_range(_1X1_RED) == 0.0

    def test_zero_for_2x2_black(self):
        # all identical black pixels -> no range
        assert qoi_luminance_range(_2X2_BLACK) == 0.0

    def test_positive_for_gradient(self):
        # gradient has varied luminance
        assert qoi_luminance_range(_4X1_GRAD) > 0

    def test_nonnegative(self):
        assert qoi_luminance_range(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_luminance_range(_4X1_GRAD) == qoi_luminance_range(_4X1_GRAD)
