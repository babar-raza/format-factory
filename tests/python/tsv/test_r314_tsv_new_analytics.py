"""
Sprint 50 — 5 new TSV analytics functions.
Tests: tsv_file_size_bytes, tsv_unique_value_count, tsv_max_row_length,
       tsv_min_row_length, tsv_row_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_file_size_bytes,
    tsv_unique_value_count,
    tsv_max_row_length,
    tsv_min_row_length,
    tsv_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.tsv")
_MULTI = str(_SAMPLES / "multi-column.tsv")
_SINGLE = str(_SAMPLES / "single-cell.tsv")


# --- tsv_file_size_bytes ---

def test_file_size_bytes_minimal_is_int():
    assert isinstance(tsv_file_size_bytes(_MINIMAL), int)


def test_file_size_bytes_minimal_positive():
    assert tsv_file_size_bytes(_MINIMAL) > 0


def test_file_size_bytes_multi_positive():
    assert tsv_file_size_bytes(_MULTI) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert tsv_file_size_bytes(_MINIMAL) == os.path.getsize(_MINIMAL)


# --- tsv_unique_value_count ---

def test_unique_value_count_minimal_is_int():
    assert isinstance(tsv_unique_value_count(_MINIMAL), int)


def test_unique_value_count_minimal_positive():
    assert tsv_unique_value_count(_MINIMAL) >= 1


def test_unique_value_count_multi_positive():
    assert tsv_unique_value_count(_MULTI) >= 1


def test_unique_value_count_single_positive():
    assert tsv_unique_value_count(_SINGLE) >= 1


# --- tsv_max_row_length ---

def test_max_row_length_minimal_is_int():
    assert isinstance(tsv_max_row_length(_MINIMAL), int)


def test_max_row_length_minimal_positive():
    assert tsv_max_row_length(_MINIMAL) >= 1


def test_max_row_length_multi_positive():
    assert tsv_max_row_length(_MULTI) >= 1


def test_max_row_length_ge_min():
    assert tsv_max_row_length(_MINIMAL) >= tsv_min_row_length(_MINIMAL)


# --- tsv_min_row_length ---

def test_min_row_length_minimal_is_int():
    assert isinstance(tsv_min_row_length(_MINIMAL), int)


def test_min_row_length_minimal_nonneg():
    assert tsv_min_row_length(_MINIMAL) >= 0


def test_min_row_length_multi_nonneg():
    assert tsv_min_row_length(_MULTI) >= 0


def test_min_row_length_single_nonneg():
    assert tsv_min_row_length(_SINGLE) >= 0


# --- tsv_row_count ---

def test_row_count_minimal_is_int():
    assert isinstance(tsv_row_count(_MINIMAL), int)


def test_row_count_minimal_positive():
    assert tsv_row_count(_MINIMAL) >= 1


def test_row_count_multi_positive():
    assert tsv_row_count(_MULTI) >= 1


def test_row_count_single_positive():
    assert tsv_row_count(_SINGLE) >= 1
