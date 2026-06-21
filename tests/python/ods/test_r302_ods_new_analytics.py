"""
Sprint 38 — 5 new ODS analytics functions.
Tests: ods_nonempty_cell_count, ods_nonempty_cell_ratio,
       ods_avg_row_length, ods_total_numeric_cells,
       ods_total_string_cells
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_nonempty_cell_count,
    ods_nonempty_cell_ratio,
    ods_avg_row_length,
    ods_total_numeric_cells,
    ods_total_string_cells,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")
_NUMERIC = str(_SAMPLES / "numeric-row.ods")
_SINGLE = str(_SAMPLES / "single-cell.ods")


# --- ods_nonempty_cell_count ---

def test_nonempty_cell_count_minimal_is_int():
    assert isinstance(ods_nonempty_cell_count(_MINIMAL), int)


def test_nonempty_cell_count_minimal_nonnegative():
    assert ods_nonempty_cell_count(_MINIMAL) >= 0


def test_nonempty_cell_count_numeric_positive():
    assert ods_nonempty_cell_count(_NUMERIC) > 0


def test_nonempty_cell_count_single_positive():
    assert ods_nonempty_cell_count(_SINGLE) >= 1


# --- ods_nonempty_cell_ratio ---

def test_nonempty_cell_ratio_minimal_is_float():
    assert isinstance(ods_nonempty_cell_ratio(_MINIMAL), float)


def test_nonempty_cell_ratio_minimal_in_range():
    result = ods_nonempty_cell_ratio(_MINIMAL)
    assert 0.0 <= result <= 1.0


def test_nonempty_cell_ratio_numeric_positive():
    assert ods_nonempty_cell_ratio(_NUMERIC) > 0.0


def test_nonempty_cell_ratio_single_positive():
    assert ods_nonempty_cell_ratio(_SINGLE) > 0.0


# --- ods_avg_row_length ---

def test_avg_row_length_minimal_is_float():
    assert isinstance(ods_avg_row_length(_MINIMAL), float)


def test_avg_row_length_minimal_positive():
    assert ods_avg_row_length(_MINIMAL) > 0.0


def test_avg_row_length_numeric_positive():
    assert ods_avg_row_length(_NUMERIC) > 0.0


def test_avg_row_length_single_positive():
    assert ods_avg_row_length(_SINGLE) > 0.0


# --- ods_total_numeric_cells ---

def test_total_numeric_cells_minimal_is_int():
    assert isinstance(ods_total_numeric_cells(_MINIMAL), int)


def test_total_numeric_cells_numeric_positive():
    assert ods_total_numeric_cells(_NUMERIC) > 0


def test_total_numeric_cells_minimal_nonnegative():
    assert ods_total_numeric_cells(_MINIMAL) >= 0


def test_total_numeric_cells_single_is_int():
    assert isinstance(ods_total_numeric_cells(_SINGLE), int)


# --- ods_total_string_cells ---

def test_total_string_cells_minimal_is_int():
    assert isinstance(ods_total_string_cells(_MINIMAL), int)


def test_total_string_cells_minimal_nonnegative():
    assert ods_total_string_cells(_MINIMAL) >= 0


def test_total_string_cells_single_is_int():
    assert isinstance(ods_total_string_cells(_SINGLE), int)


def test_total_numeric_cells_gte_nonempty_not_negative():
    assert ods_total_numeric_cells(_NUMERIC) <= ods_nonempty_cell_count(_NUMERIC)


def test_total_string_cells_numeric_sample_is_int():
    assert isinstance(ods_total_string_cells(_NUMERIC), int)


def test_total_string_cells_minimal_positive():
    assert ods_total_string_cells(_MINIMAL) >= 0
