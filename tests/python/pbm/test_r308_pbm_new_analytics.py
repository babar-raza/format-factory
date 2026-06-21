"""
Sprint 44 — 5 new PBM analytics functions.
Tests: pbm_col_uniformity, pbm_avg_black_per_row, pbm_black_row_count,
       pbm_file_size_bytes, pbm_max_col_black_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import (
    pbm_col_uniformity,
    pbm_avg_black_per_row,
    pbm_black_row_count,
    pbm_file_size_bytes,
    pbm_max_col_black_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_SAMPLES / "1x1-black.pbm")
_CHECKER = str(_SAMPLES / "2x2-checker.pbm")
_PATTERN = str(_SAMPLES / "3x2-pattern.pbm")


# --- pbm_col_uniformity ---

def test_col_uniformity_black_is_float():
    assert isinstance(pbm_col_uniformity(_BLACK), float)


def test_col_uniformity_black_is_one():
    # 1x1 all black — single column is uniform
    assert pbm_col_uniformity(_BLACK) == 1.0


def test_col_uniformity_checker_between_zero_and_one():
    result = pbm_col_uniformity(_CHECKER)
    assert 0.0 <= result <= 1.0


def test_col_uniformity_pattern_is_float():
    assert isinstance(pbm_col_uniformity(_PATTERN), float)


# --- pbm_avg_black_per_row ---

def test_avg_black_per_row_black_is_float():
    assert isinstance(pbm_avg_black_per_row(_BLACK), float)


def test_avg_black_per_row_black_positive():
    # 1x1 all black — average must be 1.0
    assert pbm_avg_black_per_row(_BLACK) == 1.0


def test_avg_black_per_row_checker_nonnegative():
    assert pbm_avg_black_per_row(_CHECKER) >= 0.0


def test_avg_black_per_row_pattern_positive():
    # 3x2 pattern has some black pixels
    assert pbm_avg_black_per_row(_PATTERN) >= 0.0


# --- pbm_black_row_count ---

def test_black_row_count_black_is_int():
    assert isinstance(pbm_black_row_count(_BLACK), int)


def test_black_row_count_black_is_one():
    # 1x1 all black — 1 row, all black
    assert pbm_black_row_count(_BLACK) == 1


def test_black_row_count_checker_nonneg():
    assert pbm_black_row_count(_CHECKER) >= 0


def test_black_row_count_pattern_nonneg():
    assert pbm_black_row_count(_PATTERN) >= 0


def test_black_row_count_no_exceed_height():
    from pbm import get_dimensions
    w, h = get_dimensions(_PATTERN)
    assert pbm_black_row_count(_PATTERN) <= h


# --- pbm_file_size_bytes ---

def test_file_size_bytes_black_is_int():
    assert isinstance(pbm_file_size_bytes(_BLACK), int)


def test_file_size_bytes_black_positive():
    assert pbm_file_size_bytes(_BLACK) > 0


def test_file_size_bytes_checker_positive():
    assert pbm_file_size_bytes(_CHECKER) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert pbm_file_size_bytes(_BLACK) == os.path.getsize(_BLACK)


# --- pbm_max_col_black_count ---

def test_max_col_black_count_black_is_int():
    assert isinstance(pbm_max_col_black_count(_BLACK), int)


def test_max_col_black_count_black_is_one():
    # 1x1 all black — max col black count is 1
    assert pbm_max_col_black_count(_BLACK) == 1


def test_max_col_black_count_checker_nonneg():
    assert pbm_max_col_black_count(_CHECKER) >= 0


def test_max_col_black_count_pattern_nonneg():
    assert pbm_max_col_black_count(_PATTERN) >= 0
