"""
Sprint 45 — 5 new PGM analytics functions.
Tests: pgm_col_uniformity, pgm_avg_pixel_per_row, pgm_dark_pixel_count,
       pgm_file_size_bytes, pgm_unique_pixel_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import (
    pgm_col_uniformity,
    pgm_avg_pixel_per_row,
    pgm_dark_pixel_count,
    pgm_file_size_bytes,
    pgm_unique_pixel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_SAMPLES / "1x1-white.pgm")
_GRADIENT = str(_SAMPLES / "2x2-gradient.pgm")
_RAMP = str(_SAMPLES / "3x1-ramp.pgm")


# --- pgm_col_uniformity ---

def test_col_uniformity_white_is_float():
    assert isinstance(pgm_col_uniformity(_WHITE), float)


def test_col_uniformity_white_is_one():
    # 1x1 single column of a single pixel — uniform
    assert pgm_col_uniformity(_WHITE) == 1.0


def test_col_uniformity_gradient_between_zero_and_one():
    result = pgm_col_uniformity(_GRADIENT)
    assert 0.0 <= result <= 1.0


def test_col_uniformity_ramp_is_float():
    assert isinstance(pgm_col_uniformity(_RAMP), float)


# --- pgm_avg_pixel_per_row ---

def test_avg_pixel_per_row_white_is_float():
    assert isinstance(pgm_avg_pixel_per_row(_WHITE), float)


def test_avg_pixel_per_row_white_nonneg():
    assert pgm_avg_pixel_per_row(_WHITE) >= 0.0


def test_avg_pixel_per_row_gradient_nonneg():
    assert pgm_avg_pixel_per_row(_GRADIENT) >= 0.0


def test_avg_pixel_per_row_ramp_nonneg():
    assert pgm_avg_pixel_per_row(_RAMP) >= 0.0


# --- pgm_dark_pixel_count ---

def test_dark_pixel_count_white_is_int():
    assert isinstance(pgm_dark_pixel_count(_WHITE), int)


def test_dark_pixel_count_white_nonneg():
    assert pgm_dark_pixel_count(_WHITE) >= 0


def test_dark_pixel_count_gradient_nonneg():
    assert pgm_dark_pixel_count(_GRADIENT) >= 0


def test_dark_pixel_count_ramp_nonneg():
    assert pgm_dark_pixel_count(_RAMP) >= 0


# --- pgm_file_size_bytes ---

def test_file_size_bytes_white_is_int():
    assert isinstance(pgm_file_size_bytes(_WHITE), int)


def test_file_size_bytes_white_positive():
    assert pgm_file_size_bytes(_WHITE) > 0


def test_file_size_bytes_gradient_positive():
    assert pgm_file_size_bytes(_GRADIENT) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert pgm_file_size_bytes(_WHITE) == os.path.getsize(_WHITE)


# --- pgm_unique_pixel_count ---

def test_unique_pixel_count_white_is_int():
    assert isinstance(pgm_unique_pixel_count(_WHITE), int)


def test_unique_pixel_count_white_positive():
    assert pgm_unique_pixel_count(_WHITE) >= 1


def test_unique_pixel_count_gradient_positive():
    assert pgm_unique_pixel_count(_GRADIENT) >= 1


def test_unique_pixel_count_ramp_positive():
    assert pgm_unique_pixel_count(_RAMP) >= 1
