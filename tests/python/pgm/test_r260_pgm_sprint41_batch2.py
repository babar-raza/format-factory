"""Tests for PGM Sprint 41 batch 2 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_COL_UNIF-001  (Pgm Col Uniformity)
  GAP-PGM-FOSS-PGM_AVG_PIXE-001  (Pgm Avg Pixel Per Row)
  GAP-PGM-FOSS-PGM_FILE_SIZ-001  (Pgm File Size Bytes)
  GAP-PGM-FOSS-PGM_UNIQUE_P-001  (Pgm Unique Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_avg_pixel_per_row,
    pgm_col_uniformity,
    pgm_file_size_bytes,
    pgm_unique_pixel_count,
)

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")


class TestPgmColUniformity:
    def test_return_type(self):
        assert isinstance(pgm_col_uniformity(_1X1_WHITE), float)

    def test_exact_1_0_for_1x1_white(self):
        assert pgm_col_uniformity(_1X1_WHITE) == 1.0

    def test_exact_0_0_for_2x2_gradient(self):
        assert pgm_col_uniformity(_2X2_GRADIENT) == 0.0

    def test_nonnegative(self):
        assert pgm_col_uniformity(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_col_uniformity(_1X1_WHITE) == pgm_col_uniformity(_1X1_WHITE)


class TestPgmAvgPixelPerRow:
    def test_return_type(self):
        assert isinstance(pgm_avg_pixel_per_row(_1X1_WHITE), float)

    def test_exact_255_0_for_1x1_white(self):
        assert pgm_avg_pixel_per_row(_1X1_WHITE) == 255.0

    def test_exact_127_5_for_2x2_gradient(self):
        assert pgm_avg_pixel_per_row(_2X2_GRADIENT) == 127.5

    def test_nonnegative(self):
        assert pgm_avg_pixel_per_row(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_avg_pixel_per_row(_1X1_WHITE) == pgm_avg_pixel_per_row(_1X1_WHITE)


class TestPgmFileSizeBytes:
    def test_return_type(self):
        assert isinstance(pgm_file_size_bytes(_1X1_WHITE), int)

    def test_exact_19_for_1x1_white(self):
        assert pgm_file_size_bytes(_1X1_WHITE) == 19

    def test_exact_29_for_2x2_gradient(self):
        assert pgm_file_size_bytes(_2X2_GRADIENT) == 29

    def test_positive(self):
        assert pgm_file_size_bytes(_1X1_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_file_size_bytes(_1X1_WHITE) == pgm_file_size_bytes(_1X1_WHITE)


class TestPgmUniquePixelCount:
    def test_return_type(self):
        assert isinstance(pgm_unique_pixel_count(_1X1_WHITE), int)

    def test_exact_1_for_1x1_white(self):
        assert pgm_unique_pixel_count(_1X1_WHITE) == 1

    def test_exact_4_for_2x2_gradient(self):
        assert pgm_unique_pixel_count(_2X2_GRADIENT) == 4

    def test_positive(self):
        assert pgm_unique_pixel_count(_1X1_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_unique_pixel_count(_1X1_WHITE) == pgm_unique_pixel_count(_1X1_WHITE)
