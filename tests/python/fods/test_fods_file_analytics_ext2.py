"""Tests for 6 new functions in fods_file_analytics (ext2 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.fods_file_analytics import (
    fods_file_min_sheet_row_count,
    fods_file_avg_sheet_row_count,
    fods_file_has_single_sheet,
    fods_file_sheet_names_sorted,
    fods_file_first_sheet_row_count,
    fods_file_last_sheet_row_count,
)

VALID = _REPO / "samples" / "by-format" / "fods" / "valid"
SIMPLE = VALID / "simple.fods"
MULTI = VALID / "multi-sheet-data.fods"   # 3 sheets: Products(4r), Orders(3r), Summary(1r)
MUTATION = VALID / "mutation-coverage.fods"  # 2 sheets: ValueTypes(3r), EmptySheet(0r)


# --- fods_file_min_sheet_row_count ---

def test_min_sheet_row_count_multi():
    # sheets have 4, 3, 1 rows → min = 1
    assert fods_file_min_sheet_row_count(MULTI) == 1

def test_min_sheet_row_count_mutation():
    # sheets have 3, 0 rows → min = 0
    assert fods_file_min_sheet_row_count(MUTATION) == 0

def test_min_sheet_row_count_type():
    result = fods_file_min_sheet_row_count(SIMPLE)
    assert isinstance(result, int)


# --- fods_file_avg_sheet_row_count ---

def test_avg_sheet_row_count_multi():
    # (4 + 3 + 1) / 3 = 8/3 ≈ 2.667
    result = fods_file_avg_sheet_row_count(MULTI)
    assert abs(result - 8/3) < 0.01

def test_avg_sheet_row_count_mutation():
    # (3 + 0) / 2 = 1.5
    assert fods_file_avg_sheet_row_count(MUTATION) == 1.5

def test_avg_sheet_row_count_type():
    result = fods_file_avg_sheet_row_count(SIMPLE)
    assert isinstance(result, float)


# --- fods_file_has_single_sheet ---

def test_has_single_sheet_multi():
    # multi-sheet-data has 3 sheets → False
    assert fods_file_has_single_sheet(MULTI) is False

def test_has_single_sheet_mutation():
    # mutation-coverage has 2 sheets → False
    assert fods_file_has_single_sheet(MUTATION) is False

def test_has_single_sheet_simple():
    result = fods_file_has_single_sheet(SIMPLE)
    assert isinstance(result, bool)


# --- fods_file_sheet_names_sorted ---

def test_sheet_names_sorted_multi():
    names = fods_file_sheet_names_sorted(MULTI)
    assert names == sorted(names)

def test_sheet_names_sorted_multi_content():
    names = fods_file_sheet_names_sorted(MULTI)
    assert set(names) == {"Orders", "Products", "Summary"}

def test_sheet_names_sorted_returns_list():
    result = fods_file_sheet_names_sorted(SIMPLE)
    assert isinstance(result, list)


# --- fods_file_first_sheet_row_count ---

def test_first_sheet_row_count_multi():
    # first sheet is Products with 4 rows
    assert fods_file_first_sheet_row_count(MULTI) == 4

def test_first_sheet_row_count_mutation():
    # first sheet is ValueTypes with 3 rows
    assert fods_file_first_sheet_row_count(MUTATION) == 3

def test_first_sheet_row_count_type():
    result = fods_file_first_sheet_row_count(SIMPLE)
    assert isinstance(result, int)


# --- fods_file_last_sheet_row_count ---

def test_last_sheet_row_count_multi():
    # last sheet is Summary with 1 row
    assert fods_file_last_sheet_row_count(MULTI) == 1

def test_last_sheet_row_count_mutation():
    # last sheet is EmptySheet with 0 rows
    assert fods_file_last_sheet_row_count(MUTATION) == 0

def test_last_sheet_row_count_type():
    result = fods_file_last_sheet_row_count(SIMPLE)
    assert isinstance(result, int)
