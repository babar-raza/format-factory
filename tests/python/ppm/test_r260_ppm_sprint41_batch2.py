"""Tests for PPM Sprint 41 batch 2 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_FILE_SIZ-001  (Ppm File Size Bytes)
  GAP-PPM-FOSS-PPM_UNIQUE_P-001  (Ppm Unique Pixel Count)
  GAP-PPM-FOSS-PPM_RED_DOMI-001  (Ppm Red Dominant Count)
  GAP-PPM-FOSS-PPM_AVG_RED_-001  (Ppm Avg Red Channel)
  GAP-PPM-FOSS-PPM_COL_UNIF-001  (Ppm Col Uniformity)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_avg_red_channel,
    ppm_col_uniformity,
    ppm_file_size_bytes,
    ppm_red_dominant_count,
    ppm_unique_pixel_count,
)

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRADIENT = str(_DIR / "3x1-gradient.ppm")


class TestPpmFileSizeBytes:
    def test_return_type(self):
        assert isinstance(ppm_file_size_bytes(_1X1_RED), int)

    def test_exact_19_for_1x1_red(self):
        assert ppm_file_size_bytes(_1X1_RED) == 19

    def test_exact_47_for_2x2_rgbw(self):
        assert ppm_file_size_bytes(_2X2_RGBW) == 47

    def test_positive(self):
        assert ppm_file_size_bytes(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_file_size_bytes(_1X1_RED) == ppm_file_size_bytes(_1X1_RED)


class TestPpmUniquePixelCount:
    def test_return_type(self):
        assert isinstance(ppm_unique_pixel_count(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_unique_pixel_count(_1X1_RED) == 1

    def test_exact_4_for_2x2_rgbw(self):
        assert ppm_unique_pixel_count(_2X2_RGBW) == 4

    def test_positive(self):
        assert ppm_unique_pixel_count(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_unique_pixel_count(_1X1_RED) == ppm_unique_pixel_count(_1X1_RED)


class TestPpmRedDominantCount:
    def test_return_type(self):
        assert isinstance(ppm_red_dominant_count(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_red_dominant_count(_1X1_RED) == 1

    def test_nonnegative(self):
        assert ppm_red_dominant_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_red_dominant_count(_1X1_RED) == ppm_red_dominant_count(_1X1_RED)


class TestPpmAvgRedChannel:
    def test_return_type(self):
        assert isinstance(ppm_avg_red_channel(_1X1_RED), float)

    def test_exact_255_0_for_1x1_red(self):
        assert ppm_avg_red_channel(_1X1_RED) == 255.0

    def test_exact_127_5_for_2x2_rgbw(self):
        assert ppm_avg_red_channel(_2X2_RGBW) == 127.5

    def test_nonnegative(self):
        assert ppm_avg_red_channel(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_avg_red_channel(_1X1_RED) == ppm_avg_red_channel(_1X1_RED)


class TestPpmColUniformity:
    def test_return_type(self):
        assert isinstance(ppm_col_uniformity(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        assert ppm_col_uniformity(_1X1_RED) == 1.0

    def test_exact_0_0_for_2x2_rgbw(self):
        assert ppm_col_uniformity(_2X2_RGBW) == 0.0

    def test_nonnegative(self):
        assert ppm_col_uniformity(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_col_uniformity(_1X1_RED) == ppm_col_uniformity(_1X1_RED)
