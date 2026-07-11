"""Tests for Gnumeric sheet analytics extension functions (batch 2) in gnumeric_sheet_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_sheet_analytics import (
    gnumeric_has_data,
    gnumeric_unique_value_count,
    gnumeric_sheet_names_sorted,
    gnumeric_total_value_count,
    gnumeric_has_multiple_sheets,
    gnumeric_max_sheet_cell_count,
)

SAMPLES = Path("samples/by-format/gnumeric")
EMPTY   = SAMPLES / "empty-sheet.gnumeric"        # 1 sheet 'Empty', 0 cells
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"  # 1 sheet 'Sheet1', 1 cell 'Hello'
MULTI   = SAMPLES / "multi-cell-basic.gnumeric"    # 1 sheet 'Sheet1', 4 cells: Name,Score,Alice,42


# gnumeric_has_data
def test_has_data_empty():
    assert gnumeric_has_data(EMPTY) is False

def test_has_data_minimal():
    assert gnumeric_has_data(MINIMAL) is True

def test_has_data_multi():
    assert gnumeric_has_data(MULTI) is True

def test_has_data_returns_bool():
    assert isinstance(gnumeric_has_data(MINIMAL), bool)


# gnumeric_unique_value_count
def test_unique_value_count_empty():
    assert gnumeric_unique_value_count(EMPTY) == 0

def test_unique_value_count_minimal():
    assert gnumeric_unique_value_count(MINIMAL) == 1

def test_unique_value_count_multi():
    assert gnumeric_unique_value_count(MULTI) == 4

def test_unique_value_count_returns_int():
    assert isinstance(gnumeric_unique_value_count(MINIMAL), int)


# gnumeric_sheet_names_sorted
def test_sheet_names_sorted_minimal():
    assert gnumeric_sheet_names_sorted(MINIMAL) == ["Sheet1"]

def test_sheet_names_sorted_returns_list():
    assert isinstance(gnumeric_sheet_names_sorted(MINIMAL), list)


# gnumeric_total_value_count
def test_total_value_count_empty():
    assert gnumeric_total_value_count(EMPTY) == 0

def test_total_value_count_minimal():
    assert gnumeric_total_value_count(MINIMAL) == 1

def test_total_value_count_multi():
    assert gnumeric_total_value_count(MULTI) == 4

def test_total_value_count_returns_int():
    assert isinstance(gnumeric_total_value_count(MINIMAL), int)


# gnumeric_has_multiple_sheets
def test_has_multiple_sheets_minimal():
    assert gnumeric_has_multiple_sheets(MINIMAL) is False

def test_has_multiple_sheets_empty():
    assert gnumeric_has_multiple_sheets(EMPTY) is False

def test_has_multiple_sheets_returns_bool():
    assert isinstance(gnumeric_has_multiple_sheets(MINIMAL), bool)


# gnumeric_max_sheet_cell_count
def test_max_sheet_cell_count_empty():
    assert gnumeric_max_sheet_cell_count(EMPTY) == 0

def test_max_sheet_cell_count_minimal():
    assert gnumeric_max_sheet_cell_count(MINIMAL) == 1

def test_max_sheet_cell_count_multi():
    assert gnumeric_max_sheet_cell_count(MULTI) == 4

def test_max_sheet_cell_count_returns_int():
    assert isinstance(gnumeric_max_sheet_cell_count(MINIMAL), int)
