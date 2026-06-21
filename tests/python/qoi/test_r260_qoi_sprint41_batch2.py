"""Tests for QOI Sprint 41 batch 2 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_RED_CHAN-001  (Qoi Red Channel Avg)
  GAP-QOI-FOSS-QOI_ALPHA_PI-001  (Qoi Alpha Pixel Count)
  GAP-QOI-FOSS-QOI_FILE_SIZ-001  (Qoi File Size Bytes)
  GAP-QOI-FOSS-QOI_AVG_RED_-001  (Qoi Avg Red Channel)
  GAP-QOI-FOSS-QOI_AVG_GREE-001  (Qoi Avg Green Channel)
  GAP-QOI-FOSS-QOI_COL_UNIF-001  (Qoi Col Uniformity)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_alpha_pixel_count,
    qoi_avg_green_channel,
    qoi_avg_red_channel,
    qoi_col_uniformity,
    qoi_file_size_bytes,
    qoi_red_channel_avg,
)

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")
_2X2_BLACK = str(_DIR / "2x2-black.qoi")
_4X1_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiRedChannelAvg:
    def test_return_type(self):
        assert isinstance(qoi_red_channel_avg(_1X1_RED), float)

    def test_exact_255_0_for_1x1_red(self):
        assert qoi_red_channel_avg(_1X1_RED) == 255.0

    def test_exact_0_0_for_2x2_black(self):
        assert qoi_red_channel_avg(_2X2_BLACK) == 0.0

    def test_nonnegative(self):
        assert qoi_red_channel_avg(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_red_channel_avg(_1X1_RED) == qoi_red_channel_avg(_1X1_RED)


class TestQoiAlphaPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_alpha_pixel_count(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        assert qoi_alpha_pixel_count(_1X1_RED) == 0

    def test_zero_for_2x2_black(self):
        assert qoi_alpha_pixel_count(_2X2_BLACK) == 0

    def test_nonnegative(self):
        assert qoi_alpha_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_alpha_pixel_count(_1X1_RED) == qoi_alpha_pixel_count(_1X1_RED)


class TestQoiFileSizeBytes:
    def test_return_type(self):
        assert isinstance(qoi_file_size_bytes(_1X1_RED), int)

    def test_exact_27_for_1x1_red(self):
        assert qoi_file_size_bytes(_1X1_RED) == 27

    def test_exact_23_for_2x2_black(self):
        assert qoi_file_size_bytes(_2X2_BLACK) == 23

    def test_positive(self):
        assert qoi_file_size_bytes(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert qoi_file_size_bytes(_1X1_RED) == qoi_file_size_bytes(_1X1_RED)


class TestQoiAvgRedChannel:
    def test_return_type(self):
        assert isinstance(qoi_avg_red_channel(_1X1_RED), float)

    def test_exact_255_0_for_1x1_red(self):
        assert qoi_avg_red_channel(_1X1_RED) == 255.0

    def test_exact_0_0_for_2x2_black(self):
        assert qoi_avg_red_channel(_2X2_BLACK) == 0.0

    def test_nonnegative(self):
        assert qoi_avg_red_channel(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_avg_red_channel(_1X1_RED) == qoi_avg_red_channel(_1X1_RED)


class TestQoiAvgGreenChannel:
    def test_return_type(self):
        assert isinstance(qoi_avg_green_channel(_1X1_RED), float)

    def test_exact_0_0_for_1x1_red(self):
        assert qoi_avg_green_channel(_1X1_RED) == 0.0

    def test_exact_0_0_for_2x2_black(self):
        assert qoi_avg_green_channel(_2X2_BLACK) == 0.0

    def test_nonnegative(self):
        assert qoi_avg_green_channel(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_avg_green_channel(_1X1_RED) == qoi_avg_green_channel(_1X1_RED)


class TestQoiColUniformity:
    def test_return_type(self):
        assert isinstance(qoi_col_uniformity(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        assert qoi_col_uniformity(_1X1_RED) == 1.0

    def test_exact_1_0_for_2x2_black(self):
        assert qoi_col_uniformity(_2X2_BLACK) == 1.0

    def test_nonnegative(self):
        assert qoi_col_uniformity(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_col_uniformity(_1X1_RED) == qoi_col_uniformity(_1X1_RED)
