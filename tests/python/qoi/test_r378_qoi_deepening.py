"""Tests for QOI product deepening sprint 149.

New functions:
  qoi_width_times_channels  — canvas width multiplied by channel count (3 or 4)
  qoi_non_black_pixel_count — count of pixels with at least one non-zero RGB channel
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_width_times_channels, qoi_non_black_pixel_count

_RED = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi")
_BLACK = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi")
_GRAD = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi")


class TestQoiWidthTimesChannels:
    def test_return_type(self):
        assert isinstance(qoi_width_times_channels(_RED), int)

    def test_exact_4_for_red(self):
        # 1x1-red.qoi: width=1, channels=4 → 1*4=4
        assert qoi_width_times_channels(_RED) == 4

    def test_exact_8_for_black(self):
        # 2x2-black.qoi: width=2, channels=4 → 2*4=8
        assert qoi_width_times_channels(_BLACK) == 8

    def test_exact_12_for_gradient(self):
        # 4x1-gradient.qoi: width=4, channels=3 → 4*3=12
        assert qoi_width_times_channels(_GRAD) == 12

    def test_positive(self):
        assert qoi_width_times_channels(_RED) > 0

    def test_consistent(self):
        assert qoi_width_times_channels(_GRAD) == qoi_width_times_channels(_GRAD)


class TestQoiNonBlackPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_non_black_pixel_count(_RED), int)

    def test_exact_1_for_red(self):
        # 1x1-red.qoi: 1 pixel (255,0,0) → non-black = 1
        assert qoi_non_black_pixel_count(_RED) == 1

    def test_zero_for_black(self):
        # 2x2-black.qoi: all (0,0,0) → non-black = 0
        assert qoi_non_black_pixel_count(_BLACK) == 0

    def test_exact_3_for_gradient(self):
        # 4x1-gradient: (0,0,0),(85,85,85),(170,170,170),(255,255,255) → 3 non-black
        assert qoi_non_black_pixel_count(_GRAD) == 3

    def test_nonnegative(self):
        assert qoi_non_black_pixel_count(_RED) >= 0

    def test_consistent(self):
        assert qoi_non_black_pixel_count(_GRAD) == qoi_non_black_pixel_count(_GRAD)
