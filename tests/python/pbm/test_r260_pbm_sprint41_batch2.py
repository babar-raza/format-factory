"""Tests for PBM Sprint 41 batch 2 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_COL_UNIF-001  (Pbm Col Uniformity)
  GAP-PBM-FOSS-PBM_AVG_BLAC-001  (Pbm Avg Black Per Row)
  GAP-PBM-FOSS-PBM_BLACK_RO-001  (Pbm Black Row Count)
  GAP-PBM-FOSS-PBM_FILE_SIZ-001  (Pbm File Size Bytes)
  GAP-PBM-FOSS-PBM_MAX_COL_-001  (Pbm Max Col Black Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_avg_black_per_row,
    pbm_black_row_count,
    pbm_col_uniformity,
    pbm_file_size_bytes,
    pbm_max_col_black_count,
)

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECKER = str(_DIR / "2x2-checker.pbm")
_3X2_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmColUniformity:
    def test_return_type(self):
        assert isinstance(pbm_col_uniformity(_1X1_BLACK), float)

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_col_uniformity(_1X1_BLACK) == 1.0

    def test_exact_0_0_for_2x2_checker(self):
        assert pbm_col_uniformity(_2X2_CHECKER) == 0.0

    def test_nonnegative(self):
        assert pbm_col_uniformity(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_col_uniformity(_1X1_BLACK) == pbm_col_uniformity(_1X1_BLACK)


class TestPbmAvgBlackPerRow:
    def test_return_type(self):
        assert isinstance(pbm_avg_black_per_row(_1X1_BLACK), float)

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_avg_black_per_row(_1X1_BLACK) == 1.0

    def test_exact_1_0_for_2x2_checker(self):
        assert pbm_avg_black_per_row(_2X2_CHECKER) == 1.0

    def test_nonnegative(self):
        assert pbm_avg_black_per_row(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_avg_black_per_row(_1X1_BLACK) == pbm_avg_black_per_row(_1X1_BLACK)


class TestPbmBlackRowCount:
    def test_return_type(self):
        assert isinstance(pbm_black_row_count(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_black_row_count(_1X1_BLACK) == 1

    def test_zero_for_2x2_checker(self):
        assert pbm_black_row_count(_2X2_CHECKER) == 0

    def test_nonnegative(self):
        assert pbm_black_row_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_black_row_count(_1X1_BLACK) == pbm_black_row_count(_1X1_BLACK)


class TestPbmFileSizeBytes:
    def test_return_type(self):
        assert isinstance(pbm_file_size_bytes(_1X1_BLACK), int)

    def test_exact_12_for_1x1_black(self):
        assert pbm_file_size_bytes(_1X1_BLACK) == 12

    def test_exact_19_for_2x2_checker(self):
        assert pbm_file_size_bytes(_2X2_CHECKER) == 19

    def test_positive(self):
        assert pbm_file_size_bytes(_1X1_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_file_size_bytes(_1X1_BLACK) == pbm_file_size_bytes(_1X1_BLACK)


class TestPbmMaxColBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_max_col_black_count(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_max_col_black_count(_1X1_BLACK) == 1

    def test_exact_1_for_2x2_checker(self):
        assert pbm_max_col_black_count(_2X2_CHECKER) == 1

    def test_nonnegative(self):
        assert pbm_max_col_black_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_max_col_black_count(_1X1_BLACK) == pbm_max_col_black_count(_1X1_BLACK)
