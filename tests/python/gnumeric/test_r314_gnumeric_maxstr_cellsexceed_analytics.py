"""
Tests for Sprint r314: gnumeric_max_string_cell_count, gnumeric_total_cells_exceed_sheets.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_max_string_cell_count,
    gnumeric_total_cells_exceed_sheets,
)

_GNUM = _REPO / "samples" / "by-format" / "gnumeric"


# --- gnumeric_max_string_cell_count ---

def test_gnumeric_max_string_cell_count_empty_zero():
    assert gnumeric_max_string_cell_count(_GNUM / "empty-sheet.gnumeric") == 0


def test_gnumeric_max_string_cell_count_minimal_one():
    assert gnumeric_max_string_cell_count(_GNUM / "minimal-spreadsheet.gnumeric") == 1


def test_gnumeric_max_string_cell_count_multi_four():
    assert gnumeric_max_string_cell_count(_GNUM / "multi-cell-basic.gnumeric") == 4


def test_gnumeric_max_string_cell_count_returns_int_empty():
    assert isinstance(gnumeric_max_string_cell_count(_GNUM / "empty-sheet.gnumeric"), int)


def test_gnumeric_max_string_cell_count_returns_int_multi():
    assert isinstance(gnumeric_max_string_cell_count(_GNUM / "multi-cell-basic.gnumeric"), int)


def test_gnumeric_max_string_cell_count_all_three_distinct():
    results = [
        gnumeric_max_string_cell_count(_GNUM / "empty-sheet.gnumeric"),
        gnumeric_max_string_cell_count(_GNUM / "minimal-spreadsheet.gnumeric"),
        gnumeric_max_string_cell_count(_GNUM / "multi-cell-basic.gnumeric"),
    ]
    assert results == [0, 1, 4]


# --- gnumeric_total_cells_exceed_sheets ---

def test_gnumeric_total_cells_exceed_sheets_empty_false():
    # 0 cells, 1 sheet → False
    assert gnumeric_total_cells_exceed_sheets(_GNUM / "empty-sheet.gnumeric") is False


def test_gnumeric_total_cells_exceed_sheets_minimal_false():
    # 1 cell, 1 sheet → False (not strictly greater)
    assert gnumeric_total_cells_exceed_sheets(_GNUM / "minimal-spreadsheet.gnumeric") is False


def test_gnumeric_total_cells_exceed_sheets_multi_true():
    # 4 cells, 1 sheet → True
    assert gnumeric_total_cells_exceed_sheets(_GNUM / "multi-cell-basic.gnumeric") is True


def test_gnumeric_total_cells_exceed_sheets_returns_bool_empty():
    assert isinstance(gnumeric_total_cells_exceed_sheets(_GNUM / "empty-sheet.gnumeric"), bool)


def test_gnumeric_total_cells_exceed_sheets_returns_bool_multi():
    assert isinstance(gnumeric_total_cells_exceed_sheets(_GNUM / "multi-cell-basic.gnumeric"), bool)


def test_gnumeric_total_cells_exceed_sheets_all_three():
    results = [
        gnumeric_total_cells_exceed_sheets(_GNUM / "empty-sheet.gnumeric"),
        gnumeric_total_cells_exceed_sheets(_GNUM / "minimal-spreadsheet.gnumeric"),
        gnumeric_total_cells_exceed_sheets(_GNUM / "multi-cell-basic.gnumeric"),
    ]
    assert results == [False, False, True]
