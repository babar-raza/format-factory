"""Tests for extended DIF stats functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_stats import (
    dif_total_cell_count,
    dif_min_row_width,
    dif_has_string_cells,
    dif_file_numeric_cell_count,
    dif_title_length,
    dif_all_cells_numeric,
)

SAMPLES = Path("samples/by-format/dif/valid")
MINIMAL = SAMPLES / "minimal-2x2.dif"      # title='minimal', 8 cells, has strings+numerics
NUMERIC = SAMPLES / "numeric-row.dif"       # title='numeric-row', 3 numeric cells
SINGLE = SAMPLES / "single-cell.dif"        # title='single-cell', 1 numeric cell


# --- dif_total_cell_count ---

def test_total_cell_count_minimal():
    assert dif_total_cell_count(MINIMAL) == 8


def test_total_cell_count_numeric():
    assert dif_total_cell_count(NUMERIC) == 3


def test_total_cell_count_single():
    assert dif_total_cell_count(SINGLE) == 1


def test_total_cell_count_returns_int():
    assert isinstance(dif_total_cell_count(MINIMAL), int)


# --- dif_min_row_width ---

def test_min_row_width_minimal():
    assert dif_min_row_width(MINIMAL) == 8


def test_min_row_width_numeric():
    assert dif_min_row_width(NUMERIC) == 3


def test_min_row_width_single():
    assert dif_min_row_width(SINGLE) == 1


def test_min_row_width_returns_int():
    assert isinstance(dif_min_row_width(MINIMAL), int)


# --- dif_has_string_cells ---

def test_has_string_cells_minimal():
    assert dif_has_string_cells(MINIMAL) is True


def test_has_string_cells_numeric():
    assert dif_has_string_cells(NUMERIC) is False


def test_has_string_cells_single():
    assert dif_has_string_cells(SINGLE) is False


def test_has_string_cells_returns_bool():
    assert isinstance(dif_has_string_cells(MINIMAL), bool)


# --- dif_file_numeric_cell_count ---

def test_file_numeric_cell_count_minimal():
    assert dif_file_numeric_cell_count(MINIMAL) == 2


def test_file_numeric_cell_count_numeric():
    assert dif_file_numeric_cell_count(NUMERIC) == 3


def test_file_numeric_cell_count_single():
    assert dif_file_numeric_cell_count(SINGLE) == 1


def test_file_numeric_cell_count_returns_int():
    assert isinstance(dif_file_numeric_cell_count(MINIMAL), int)


# --- dif_title_length ---

def test_title_length_minimal():
    assert dif_title_length(MINIMAL) == 7  # 'minimal'


def test_title_length_numeric():
    assert dif_title_length(NUMERIC) == 11  # 'numeric-row'


def test_title_length_single():
    assert dif_title_length(SINGLE) == 11  # 'single-cell'


def test_title_length_returns_int():
    assert isinstance(dif_title_length(MINIMAL), int)


# --- dif_all_cells_numeric ---

def test_all_cells_numeric_minimal():
    assert dif_all_cells_numeric(MINIMAL) is False


def test_all_cells_numeric_numeric():
    assert dif_all_cells_numeric(NUMERIC) is True


def test_all_cells_numeric_single():
    assert dif_all_cells_numeric(SINGLE) is True


def test_all_cells_numeric_returns_bool():
    assert isinstance(dif_all_cells_numeric(MINIMAL), bool)
