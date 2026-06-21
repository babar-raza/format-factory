"""
Sprint 42 — 5 new Gnumeric analytics functions.
Tests: gnumeric_nonempty_cell_count, gnumeric_nonempty_cell_ratio,
       gnumeric_avg_cell_value_length, gnumeric_total_cell_count,
       gnumeric_string_cell_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    gnumeric_nonempty_cell_count,
    gnumeric_nonempty_cell_ratio,
    gnumeric_avg_cell_value_length,
    gnumeric_total_cell_count,
    gnumeric_string_cell_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")
_EMPTY = str(_SAMPLES / "empty-sheet.gnumeric")


# --- gnumeric_nonempty_cell_count ---

def test_nonempty_cell_count_minimal_is_int():
    assert isinstance(gnumeric_nonempty_cell_count(_MINIMAL), int)


def test_nonempty_cell_count_minimal_nonnegative():
    assert gnumeric_nonempty_cell_count(_MINIMAL) >= 0


def test_nonempty_cell_count_multi_positive():
    assert gnumeric_nonempty_cell_count(_MULTI) > 0


def test_nonempty_cell_count_empty_nonnegative():
    assert gnumeric_nonempty_cell_count(_EMPTY) >= 0


# --- gnumeric_nonempty_cell_ratio ---

def test_nonempty_cell_ratio_minimal_is_float():
    assert isinstance(gnumeric_nonempty_cell_ratio(_MINIMAL), float)


def test_nonempty_cell_ratio_minimal_in_range():
    result = gnumeric_nonempty_cell_ratio(_MINIMAL)
    assert 0.0 <= result <= 1.0


def test_nonempty_cell_ratio_multi_positive():
    assert gnumeric_nonempty_cell_ratio(_MULTI) > 0.0


def test_nonempty_cell_ratio_empty_nonnegative():
    assert gnumeric_nonempty_cell_ratio(_EMPTY) >= 0.0


# --- gnumeric_avg_cell_value_length ---

def test_avg_cell_value_length_minimal_is_float():
    assert isinstance(gnumeric_avg_cell_value_length(_MINIMAL), float)


def test_avg_cell_value_length_minimal_nonnegative():
    assert gnumeric_avg_cell_value_length(_MINIMAL) >= 0.0


def test_avg_cell_value_length_multi_positive():
    assert gnumeric_avg_cell_value_length(_MULTI) > 0.0


def test_avg_cell_value_length_empty_is_zero():
    assert gnumeric_avg_cell_value_length(_EMPTY) == 0.0


# --- gnumeric_total_cell_count ---

def test_total_cell_count_minimal_is_int():
    assert isinstance(gnumeric_total_cell_count(_MINIMAL), int)


def test_total_cell_count_minimal_nonnegative():
    assert gnumeric_total_cell_count(_MINIMAL) >= 0


def test_total_cell_count_multi_positive():
    assert gnumeric_total_cell_count(_MULTI) > 0


def test_total_cell_count_empty_nonnegative():
    assert gnumeric_total_cell_count(_EMPTY) >= 0


# --- gnumeric_string_cell_count ---

def test_string_cell_count_minimal_is_int():
    assert isinstance(gnumeric_string_cell_count(_MINIMAL), int)


def test_string_cell_count_minimal_nonnegative():
    assert gnumeric_string_cell_count(_MINIMAL) >= 0


def test_string_cell_count_multi_is_int():
    assert isinstance(gnumeric_string_cell_count(_MULTI), int)


def test_string_cell_count_empty_is_zero():
    assert gnumeric_string_cell_count(_EMPTY) == 0
