"""Tests for SYLK grid-level analytics extension in sylk_value_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_value_analytics import (
    sylk_has_data,
    sylk_is_square_grid,
    sylk_grid_size,
    sylk_cell_fill_ratio,
    sylk_is_wide,
    sylk_is_tall,
)

SAMPLES = Path("samples/by-format/sylk/valid")
MINIMAL  = SAMPLES / "minimal-2x2.slk"     # rows=2, cols=2, cell_count=4
NUMERIC  = SAMPLES / "numeric-row.slk"     # rows=1, cols=3, cell_count=3
SINGLE   = SAMPLES / "single-cell.slk"     # rows=1, cols=1, cell_count=1


# --- sylk_has_data ---

def test_has_data_minimal():
    assert sylk_has_data(MINIMAL) is True


def test_has_data_numeric():
    assert sylk_has_data(NUMERIC) is True


def test_has_data_single():
    assert sylk_has_data(SINGLE) is True


def test_has_data_returns_bool():
    assert isinstance(sylk_has_data(MINIMAL), bool)


# --- sylk_is_square_grid ---

def test_is_square_grid_minimal():
    # rows=2, cols=2 → True
    assert sylk_is_square_grid(MINIMAL) is True


def test_is_square_grid_numeric():
    # rows=1, cols=3 → False
    assert sylk_is_square_grid(NUMERIC) is False


def test_is_square_grid_single():
    # rows=1, cols=1 → True
    assert sylk_is_square_grid(SINGLE) is True


def test_is_square_grid_returns_bool():
    assert isinstance(sylk_is_square_grid(MINIMAL), bool)


# --- sylk_grid_size ---

def test_grid_size_minimal():
    # 2 * 2 = 4
    assert sylk_grid_size(MINIMAL) == 4


def test_grid_size_numeric():
    # 1 * 3 = 3
    assert sylk_grid_size(NUMERIC) == 3


def test_grid_size_single():
    # 1 * 1 = 1
    assert sylk_grid_size(SINGLE) == 1


def test_grid_size_returns_int():
    assert isinstance(sylk_grid_size(MINIMAL), int)


def test_grid_size_positive():
    assert sylk_grid_size(MINIMAL) > 0


# --- sylk_cell_fill_ratio ---

def test_cell_fill_ratio_minimal():
    # 4 cells / 4 grid = 1.0
    assert sylk_cell_fill_ratio(MINIMAL) == 1.0


def test_cell_fill_ratio_numeric():
    # 3 cells / 3 grid = 1.0
    assert sylk_cell_fill_ratio(NUMERIC) == 1.0


def test_cell_fill_ratio_single():
    # 1 / 1 = 1.0
    assert sylk_cell_fill_ratio(SINGLE) == 1.0


def test_cell_fill_ratio_returns_float():
    assert isinstance(sylk_cell_fill_ratio(MINIMAL), float)


# --- sylk_is_wide ---

def test_is_wide_numeric():
    # cols=3 > rows=1 → True
    assert sylk_is_wide(NUMERIC) is True


def test_is_wide_minimal():
    # cols=2 == rows=2 → False
    assert sylk_is_wide(MINIMAL) is False


def test_is_wide_single():
    # cols=1 == rows=1 → False
    assert sylk_is_wide(SINGLE) is False


def test_is_wide_returns_bool():
    assert isinstance(sylk_is_wide(MINIMAL), bool)


# --- sylk_is_tall ---

def test_is_tall_minimal():
    # rows=2 == cols=2 → False
    assert sylk_is_tall(MINIMAL) is False


def test_is_tall_numeric():
    # rows=1, cols=3 → 1 < 3 → False
    assert sylk_is_tall(NUMERIC) is False


def test_is_tall_single():
    # rows=1 == cols=1 → False
    assert sylk_is_tall(SINGLE) is False


def test_is_tall_returns_bool():
    assert isinstance(sylk_is_tall(MINIMAL), bool)
