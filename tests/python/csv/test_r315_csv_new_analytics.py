"""
Sprint 51 — 5 new CSV analytics functions.
Tests: csv_file_size_bytes, csv_unique_value_count, csv_max_row_length,
       csv_min_row_length, csv_total_field_count
Note: csv conflicts with stdlib, so import via sys.path + src.python.csv
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_file_size_bytes,
    csv_unique_value_count,
    csv_max_row_length,
    csv_min_row_length,
    csv_total_field_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.csv")
_QUOTED = str(_SAMPLES / "quoted-fields.csv")
_SINGLE = str(_SAMPLES / "single-cell.csv")


# --- csv_file_size_bytes ---

def test_file_size_bytes_minimal_is_int():
    assert isinstance(csv_file_size_bytes(_MINIMAL), int)


def test_file_size_bytes_minimal_positive():
    assert csv_file_size_bytes(_MINIMAL) > 0


def test_file_size_bytes_quoted_positive():
    assert csv_file_size_bytes(_QUOTED) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert csv_file_size_bytes(_MINIMAL) == os.path.getsize(_MINIMAL)


# --- csv_unique_value_count ---

def test_unique_value_count_minimal_is_int():
    assert isinstance(csv_unique_value_count(_MINIMAL), int)


def test_unique_value_count_minimal_positive():
    assert csv_unique_value_count(_MINIMAL) >= 1


def test_unique_value_count_quoted_positive():
    assert csv_unique_value_count(_QUOTED) >= 1


def test_unique_value_count_single_positive():
    assert csv_unique_value_count(_SINGLE) >= 1


# --- csv_max_row_length ---

def test_max_row_length_minimal_is_int():
    assert isinstance(csv_max_row_length(_MINIMAL), int)


def test_max_row_length_minimal_positive():
    assert csv_max_row_length(_MINIMAL) >= 1


def test_max_row_length_quoted_positive():
    assert csv_max_row_length(_QUOTED) >= 1


def test_max_row_length_ge_min():
    assert csv_max_row_length(_MINIMAL) >= csv_min_row_length(_MINIMAL)


# --- csv_min_row_length ---

def test_min_row_length_minimal_is_int():
    assert isinstance(csv_min_row_length(_MINIMAL), int)


def test_min_row_length_minimal_nonneg():
    assert csv_min_row_length(_MINIMAL) >= 0


def test_min_row_length_single_nonneg():
    assert csv_min_row_length(_SINGLE) >= 0


def test_min_row_length_quoted_nonneg():
    assert csv_min_row_length(_QUOTED) >= 0


# --- csv_total_field_count ---

def test_total_field_count_minimal_is_int():
    assert isinstance(csv_total_field_count(_MINIMAL), int)


def test_total_field_count_minimal_positive():
    assert csv_total_field_count(_MINIMAL) >= 1


def test_total_field_count_single_positive():
    assert csv_total_field_count(_SINGLE) >= 1


def test_total_field_count_ge_max_row():
    assert csv_total_field_count(_MINIMAL) >= csv_max_row_length(_MINIMAL)
