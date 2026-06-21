"""
Sprint 49 — 5 new DIF analytics functions.
Tests: dif_file_size_bytes, dif_unique_string_count, dif_nonempty_cell_ratio,
       dif_max_row_cell_count, dif_min_row_cell_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_file_size_bytes,
    dif_unique_string_count,
    dif_nonempty_cell_ratio,
    dif_max_row_cell_count,
    dif_min_row_cell_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-2x2.dif")
_NUMERIC = str(_SAMPLES / "numeric-row.dif")
_SINGLE = str(_SAMPLES / "single-cell.dif")


# --- dif_file_size_bytes ---

def test_file_size_bytes_minimal_is_int():
    assert isinstance(dif_file_size_bytes(_MINIMAL), int)


def test_file_size_bytes_minimal_positive():
    assert dif_file_size_bytes(_MINIMAL) > 0


def test_file_size_bytes_numeric_positive():
    assert dif_file_size_bytes(_NUMERIC) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert dif_file_size_bytes(_MINIMAL) == os.path.getsize(_MINIMAL)


# --- dif_unique_string_count ---

def test_unique_string_count_minimal_is_int():
    assert isinstance(dif_unique_string_count(_MINIMAL), int)


def test_unique_string_count_minimal_nonneg():
    assert dif_unique_string_count(_MINIMAL) >= 0


def test_unique_string_count_numeric_nonneg():
    assert dif_unique_string_count(_NUMERIC) >= 0


def test_unique_string_count_single_nonneg():
    assert dif_unique_string_count(_SINGLE) >= 0


# --- dif_nonempty_cell_ratio ---

def test_nonempty_cell_ratio_minimal_is_float():
    assert isinstance(dif_nonempty_cell_ratio(_MINIMAL), float)


def test_nonempty_cell_ratio_minimal_nonneg():
    assert dif_nonempty_cell_ratio(_MINIMAL) >= 0.0


def test_nonempty_cell_ratio_at_most_one():
    assert dif_nonempty_cell_ratio(_MINIMAL) <= 1.0


def test_nonempty_cell_ratio_single_nonneg():
    assert dif_nonempty_cell_ratio(_SINGLE) >= 0.0


# --- dif_max_row_cell_count ---

def test_max_row_cell_count_minimal_is_int():
    assert isinstance(dif_max_row_cell_count(_MINIMAL), int)


def test_max_row_cell_count_minimal_positive():
    assert dif_max_row_cell_count(_MINIMAL) >= 1


def test_max_row_cell_count_numeric_positive():
    assert dif_max_row_cell_count(_NUMERIC) >= 1


def test_max_row_cell_count_single_positive():
    assert dif_max_row_cell_count(_SINGLE) >= 1


# --- dif_min_row_cell_count ---

def test_min_row_cell_count_minimal_is_int():
    assert isinstance(dif_min_row_cell_count(_MINIMAL), int)


def test_min_row_cell_count_minimal_nonneg():
    assert dif_min_row_cell_count(_MINIMAL) >= 0


def test_min_row_cell_count_numeric_nonneg():
    assert dif_min_row_cell_count(_NUMERIC) >= 0


def test_min_row_cell_count_le_max():
    assert dif_min_row_cell_count(_MINIMAL) <= dif_max_row_cell_count(_MINIMAL)
