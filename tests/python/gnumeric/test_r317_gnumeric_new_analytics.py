"""
Sprint 53 — 5 new Gnumeric analytics functions.
Tests: gnumeric_file_size_bytes, gnumeric_unique_value_count, gnumeric_max_sheet_cell_count,
       gnumeric_min_sheet_cell_count, gnumeric_avg_sheet_cell_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    gnumeric_file_size_bytes,
    gnumeric_unique_value_count,
    gnumeric_max_sheet_cell_count,
    gnumeric_min_sheet_cell_count,
    gnumeric_avg_sheet_cell_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")
_EMPTY = str(_SAMPLES / "empty-sheet.gnumeric")


# --- gnumeric_file_size_bytes ---

def test_file_size_bytes_minimal_is_int():
    assert isinstance(gnumeric_file_size_bytes(_MINIMAL), int)


def test_file_size_bytes_minimal_positive():
    assert gnumeric_file_size_bytes(_MINIMAL) > 0


def test_file_size_bytes_multi_positive():
    assert gnumeric_file_size_bytes(_MULTI) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert gnumeric_file_size_bytes(_MINIMAL) == os.path.getsize(_MINIMAL)


# --- gnumeric_unique_value_count ---

def test_unique_value_count_minimal_is_int():
    assert isinstance(gnumeric_unique_value_count(_MINIMAL), int)


def test_unique_value_count_minimal_nonneg():
    assert gnumeric_unique_value_count(_MINIMAL) >= 0


def test_unique_value_count_multi_nonneg():
    assert gnumeric_unique_value_count(_MULTI) >= 0


def test_unique_value_count_empty_is_zero():
    assert gnumeric_unique_value_count(_EMPTY) == 0


# --- gnumeric_max_sheet_cell_count ---

def test_max_sheet_cell_count_minimal_is_int():
    assert isinstance(gnumeric_max_sheet_cell_count(_MINIMAL), int)


def test_max_sheet_cell_count_minimal_nonneg():
    assert gnumeric_max_sheet_cell_count(_MINIMAL) >= 0


def test_max_sheet_cell_count_multi_nonneg():
    assert gnumeric_max_sheet_cell_count(_MULTI) >= 0


def test_max_sheet_cell_count_ge_min():
    assert gnumeric_max_sheet_cell_count(_MINIMAL) >= gnumeric_min_sheet_cell_count(_MINIMAL)


# --- gnumeric_min_sheet_cell_count ---

def test_min_sheet_cell_count_minimal_is_int():
    assert isinstance(gnumeric_min_sheet_cell_count(_MINIMAL), int)


def test_min_sheet_cell_count_minimal_nonneg():
    assert gnumeric_min_sheet_cell_count(_MINIMAL) >= 0


def test_min_sheet_cell_count_multi_nonneg():
    assert gnumeric_min_sheet_cell_count(_MULTI) >= 0


def test_min_sheet_cell_count_empty_is_zero():
    assert gnumeric_min_sheet_cell_count(_EMPTY) == 0


# --- gnumeric_avg_sheet_cell_count ---

def test_avg_sheet_cell_count_minimal_is_float():
    assert isinstance(gnumeric_avg_sheet_cell_count(_MINIMAL), float)


def test_avg_sheet_cell_count_minimal_nonneg():
    assert gnumeric_avg_sheet_cell_count(_MINIMAL) >= 0.0


def test_avg_sheet_cell_count_multi_nonneg():
    assert gnumeric_avg_sheet_cell_count(_MULTI) >= 0.0


def test_avg_sheet_cell_count_empty_is_zero():
    assert gnumeric_avg_sheet_cell_count(_EMPTY) == 0.0
