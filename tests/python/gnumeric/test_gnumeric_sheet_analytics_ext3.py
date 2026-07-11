"""Tests for gnumeric_sheet_analytics extension (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from gnumeric.gnumeric_sheet_analytics import (
    gnumeric_last_sheet_name,
    gnumeric_min_sheet_cell_count,
    gnumeric_avg_sheet_cell_count,
    gnumeric_sheets_with_cells_count,
    gnumeric_total_numeric_value_count,
    gnumeric_all_sheet_cell_counts,
)

SAMPLES = Path("samples/by-format/gnumeric")
EMPTY = SAMPLES / "empty-sheet.gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"


# --- gnumeric_last_sheet_name ---

def test_last_sheet_name_minimal():
    name = gnumeric_last_sheet_name(MINIMAL)
    assert isinstance(name, str)
    assert len(name) > 0


def test_last_sheet_name_empty():
    name = gnumeric_last_sheet_name(EMPTY)
    assert isinstance(name, str)


# --- gnumeric_min_sheet_cell_count ---

def test_min_sheet_cell_count_minimal_positive():
    result = gnumeric_min_sheet_cell_count(MINIMAL)
    assert isinstance(result, int)
    assert result >= 0


def test_min_sheet_cell_count_multi():
    result = gnumeric_min_sheet_cell_count(MULTI)
    assert result >= 0


def test_min_sheet_cell_count_leq_max():
    from gnumeric.gnumeric_sheet_analytics import gnumeric_max_sheet_cell_count
    min_val = gnumeric_min_sheet_cell_count(MINIMAL)
    max_val = gnumeric_max_sheet_cell_count(MINIMAL)
    assert min_val <= max_val


# --- gnumeric_avg_sheet_cell_count ---

def test_avg_sheet_cell_count_returns_float():
    result = gnumeric_avg_sheet_cell_count(MINIMAL)
    assert isinstance(result, float)


def test_avg_sheet_cell_count_minimal_positive():
    result = gnumeric_avg_sheet_cell_count(MINIMAL)
    assert result >= 0.0


# --- gnumeric_sheets_with_cells_count ---

def test_sheets_with_cells_count_minimal():
    result = gnumeric_sheets_with_cells_count(MINIMAL)
    assert isinstance(result, int)
    assert result >= 1


def test_sheets_with_cells_count_empty():
    result = gnumeric_sheets_with_cells_count(EMPTY)
    assert isinstance(result, int)
    assert result == 0


# --- gnumeric_total_numeric_value_count ---

def test_total_numeric_value_count_multi():
    result = gnumeric_total_numeric_value_count(MULTI)
    assert isinstance(result, int)
    assert result >= 0


def test_total_numeric_value_count_minimal():
    result = gnumeric_total_numeric_value_count(MINIMAL)
    assert isinstance(result, int)


# --- gnumeric_all_sheet_cell_counts ---

def test_all_sheet_cell_counts_returns_list():
    result = gnumeric_all_sheet_cell_counts(MINIMAL)
    assert isinstance(result, list)


def test_all_sheet_cell_counts_length():
    from gnumeric.gnumeric_sheet_analytics import gnumeric_sheet_count
    result = gnumeric_all_sheet_cell_counts(MINIMAL)
    assert len(result) == gnumeric_sheet_count(MINIMAL)


def test_all_sheet_cell_counts_values_are_ints():
    result = gnumeric_all_sheet_cell_counts(MULTI)
    assert all(isinstance(v, int) for v in result)
