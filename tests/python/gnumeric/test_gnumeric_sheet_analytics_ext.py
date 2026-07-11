"""Tests for Gnumeric sheet analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_sheet_analytics import (
    gnumeric_sheet_count,
    gnumeric_is_gnumeric,
    gnumeric_cell_count,
    gnumeric_first_sheet_name,
    gnumeric_first_sheet_cell_count,
    gnumeric_all_values,
)

SAMPLES = Path("samples/by-format/gnumeric")
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"
EMPTY = SAMPLES / "empty-sheet.gnumeric"
# minimal-spreadsheet: 1 sheet='Sheet1', 1 cell=['Hello']
# multi-cell-basic: 1 sheet='Sheet1', 4 cells=['Name','Score','Alice','42']
# empty-sheet: 1 sheet='Empty', 0 cells


# --- gnumeric_sheet_count ---

def test_sheet_count_minimal():
    assert gnumeric_sheet_count(MINIMAL) == 1


def test_sheet_count_multi():
    assert gnumeric_sheet_count(MULTI) == 1


def test_sheet_count_returns_int():
    assert isinstance(gnumeric_sheet_count(MINIMAL), int)


# --- gnumeric_is_gnumeric ---

def test_is_gnumeric_minimal():
    assert gnumeric_is_gnumeric(MINIMAL) is True


def test_is_gnumeric_empty():
    assert gnumeric_is_gnumeric(EMPTY) is True


def test_is_gnumeric_returns_bool():
    assert isinstance(gnumeric_is_gnumeric(MINIMAL), bool)


# --- gnumeric_cell_count ---

def test_cell_count_minimal():
    assert gnumeric_cell_count(MINIMAL) == 1


def test_cell_count_multi():
    assert gnumeric_cell_count(MULTI) == 4


def test_cell_count_empty():
    assert gnumeric_cell_count(EMPTY) == 0


def test_cell_count_returns_int():
    assert isinstance(gnumeric_cell_count(MINIMAL), int)


# --- gnumeric_first_sheet_name ---

def test_first_sheet_name_minimal():
    assert gnumeric_first_sheet_name(MINIMAL) == "Sheet1"


def test_first_sheet_name_empty():
    assert gnumeric_first_sheet_name(EMPTY) == "Empty"


def test_first_sheet_name_returns_str():
    assert isinstance(gnumeric_first_sheet_name(MINIMAL), str)


# --- gnumeric_first_sheet_cell_count ---

def test_first_sheet_cell_count_minimal():
    assert gnumeric_first_sheet_cell_count(MINIMAL) == 1


def test_first_sheet_cell_count_multi():
    assert gnumeric_first_sheet_cell_count(MULTI) == 4


def test_first_sheet_cell_count_empty():
    assert gnumeric_first_sheet_cell_count(EMPTY) == 0


def test_first_sheet_cell_count_returns_int():
    assert isinstance(gnumeric_first_sheet_cell_count(MINIMAL), int)


# --- gnumeric_all_values ---

def test_all_values_minimal():
    assert gnumeric_all_values(MINIMAL) == ["Hello"]


def test_all_values_multi():
    assert gnumeric_all_values(MULTI) == ["Name", "Score", "Alice", "42"]


def test_all_values_empty():
    assert gnumeric_all_values(EMPTY) == []


def test_all_values_returns_list():
    assert isinstance(gnumeric_all_values(MINIMAL), list)
