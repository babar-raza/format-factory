"""Tests for 6 new functions in sylk_value_analytics (ext2 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

from sylk.sylk_value_analytics import (
    sylk_cell_count,
    sylk_row_count,
    sylk_unique_value_count,
    sylk_numeric_cell_count,
    sylk_string_cell_count,
    sylk_last_cell_value,
)

VALID = _REPO / "samples" / "by-format" / "sylk" / "valid"
SINGLE = VALID / "single-cell.slk"
MINIMAL = VALID / "minimal-2x2.slk"
NUMERIC = VALID / "numeric-row.slk"


# --- sylk_cell_count ---

def test_cell_count_single():
    assert sylk_cell_count(SINGLE) == 1


def test_cell_count_minimal():
    assert sylk_cell_count(MINIMAL) == 4


def test_cell_count_numeric_row():
    assert sylk_cell_count(NUMERIC) == 3


# --- sylk_row_count ---

def test_row_count_single():
    assert sylk_row_count(SINGLE) == 1


def test_row_count_minimal():
    assert sylk_row_count(MINIMAL) == 2


def test_row_count_numeric():
    assert sylk_row_count(NUMERIC) == 1


# --- sylk_unique_value_count ---

def test_unique_value_count_single():
    # single-cell has value 99
    assert sylk_unique_value_count(SINGLE) == 1


def test_unique_value_count_minimal():
    # minimal has 'Name', 'Value', 'Alpha', 42 — all distinct
    assert sylk_unique_value_count(MINIMAL) == 4


def test_unique_value_count_numeric_row():
    # numeric-row has 1, 2, 3
    assert sylk_unique_value_count(NUMERIC) == 3


# --- sylk_numeric_cell_count ---

def test_numeric_cell_count_single():
    # single-cell is numeric
    assert sylk_numeric_cell_count(SINGLE) == 1


def test_numeric_cell_count_minimal():
    # minimal has 3 strings + 1 numeric (42)
    assert sylk_numeric_cell_count(MINIMAL) == 1


def test_numeric_cell_count_numeric_row():
    # numeric-row has 3 numeric cells
    assert sylk_numeric_cell_count(NUMERIC) == 3


# --- sylk_string_cell_count ---

def test_string_cell_count_single():
    # single-cell is numeric, not string
    assert sylk_string_cell_count(SINGLE) == 0


def test_string_cell_count_minimal():
    # minimal has 3 string cells
    assert sylk_string_cell_count(MINIMAL) == 3


def test_string_cell_count_numeric_row():
    # numeric-row has 0 string cells
    assert sylk_string_cell_count(NUMERIC) == 0


# --- sylk_last_cell_value ---

def test_last_cell_value_single():
    assert sylk_last_cell_value(SINGLE) == 99


def test_last_cell_value_minimal():
    # last cell is (2,2) with value 42
    assert sylk_last_cell_value(MINIMAL) == 42


def test_last_cell_value_numeric_row():
    # last cell in numeric row is 3
    assert sylk_last_cell_value(NUMERIC) == 3


def test_last_cell_value_type():
    # should return the raw value, not a string
    val = sylk_last_cell_value(NUMERIC)
    assert isinstance(val, (int, float))
