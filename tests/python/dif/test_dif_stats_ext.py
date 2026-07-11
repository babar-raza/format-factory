"""Tests for DIF stats extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_stats import (
    dif_title,
    dif_row_count,
    dif_first_row_cell_count,
    dif_has_numeric_cells,
    dif_numeric_cell_values,
    dif_cell_type_set,
)

SAMPLES = Path("samples/by-format/dif/valid")
MINIMAL = SAMPLES / "minimal-2x2.dif"
NUMERIC = SAMPLES / "numeric-row.dif"
SINGLE = SAMPLES / "single-cell.dif"
# minimal-2x2.dif: title='minimal', 1 row, 8 cells (special+string+numeric), nums=[42.0,99.0]
# numeric-row.dif: title='numeric-row', 1 row, 3 numeric cells [1.0,2.0,3.0]
# single-cell.dif: title='single-cell', 1 row, 1 numeric cell [42.0]


# --- dif_title ---

def test_title_minimal():
    assert dif_title(MINIMAL) == "minimal"


def test_title_numeric():
    assert dif_title(NUMERIC) == "numeric-row"


def test_title_single():
    assert dif_title(SINGLE) == "single-cell"


def test_title_returns_str():
    assert isinstance(dif_title(MINIMAL), str)


# --- dif_row_count ---

def test_row_count_minimal():
    assert dif_row_count(MINIMAL) == 1


def test_row_count_numeric():
    assert dif_row_count(NUMERIC) == 1


def test_row_count_returns_int():
    assert isinstance(dif_row_count(MINIMAL), int)


# --- dif_first_row_cell_count ---

def test_first_row_cell_count_minimal():
    assert dif_first_row_cell_count(MINIMAL) == 8


def test_first_row_cell_count_numeric():
    assert dif_first_row_cell_count(NUMERIC) == 3


def test_first_row_cell_count_single():
    assert dif_first_row_cell_count(SINGLE) == 1


def test_first_row_cell_count_returns_int():
    assert isinstance(dif_first_row_cell_count(MINIMAL), int)


# --- dif_has_numeric_cells ---

def test_has_numeric_cells_minimal():
    assert dif_has_numeric_cells(MINIMAL) is True


def test_has_numeric_cells_numeric():
    assert dif_has_numeric_cells(NUMERIC) is True


def test_has_numeric_cells_single():
    assert dif_has_numeric_cells(SINGLE) is True


def test_has_numeric_cells_returns_bool():
    assert isinstance(dif_has_numeric_cells(MINIMAL), bool)


# --- dif_numeric_cell_values ---

def test_numeric_cell_values_minimal():
    assert dif_numeric_cell_values(MINIMAL) == [42.0, 99.0]


def test_numeric_cell_values_numeric():
    assert dif_numeric_cell_values(NUMERIC) == [1.0, 2.0, 3.0]


def test_numeric_cell_values_single():
    assert dif_numeric_cell_values(SINGLE) == [42.0]


def test_numeric_cell_values_returns_list():
    assert isinstance(dif_numeric_cell_values(MINIMAL), list)


# --- dif_cell_type_set ---

def test_cell_type_set_minimal():
    types = dif_cell_type_set(MINIMAL)
    assert "numeric" in types
    assert "string" in types


def test_cell_type_set_numeric():
    assert dif_cell_type_set(NUMERIC) == ["numeric"]


def test_cell_type_set_returns_list():
    assert isinstance(dif_cell_type_set(MINIMAL), list)
