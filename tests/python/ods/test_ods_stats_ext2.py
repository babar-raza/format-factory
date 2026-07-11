"""Tests for ODS sheet analytics extensions in ods_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_stats import (
    ods_sheet_names_sorted,
    ods_has_single_sheet,
    ods_first_sheet_row_count,
    ods_all_sheets_named,
    ods_has_uniform_sheet_row_count,
    ods_min_sheet_row_count,
)

SAMPLES = Path("samples/by-format/ods/valid")
MINIMAL = SAMPLES / "minimal-spreadsheet.ods"   # Sheet1, 2 rows
NUMERIC = SAMPLES / "numeric-row.ods"            # Sheet1, 1 row, 3 float cells
SINGLE  = SAMPLES / "single-cell.ods"            # Sheet1, 1 row, 1 string cell


# --- ods_sheet_names_sorted ---

def test_sheet_names_sorted_minimal():
    assert ods_sheet_names_sorted(MINIMAL) == ["Sheet1"]


def test_sheet_names_sorted_numeric():
    assert ods_sheet_names_sorted(NUMERIC) == ["Sheet1"]


def test_sheet_names_sorted_single():
    assert ods_sheet_names_sorted(SINGLE) == ["Sheet1"]


def test_sheet_names_sorted_returns_list():
    assert isinstance(ods_sheet_names_sorted(MINIMAL), list)


# --- ods_has_single_sheet ---

def test_has_single_sheet_minimal():
    assert ods_has_single_sheet(MINIMAL) is True


def test_has_single_sheet_numeric():
    assert ods_has_single_sheet(NUMERIC) is True


def test_has_single_sheet_returns_bool():
    assert isinstance(ods_has_single_sheet(MINIMAL), bool)


# --- ods_first_sheet_row_count ---

def test_first_sheet_row_count_minimal():
    assert ods_first_sheet_row_count(MINIMAL) == 2


def test_first_sheet_row_count_numeric():
    assert ods_first_sheet_row_count(NUMERIC) == 1


def test_first_sheet_row_count_single():
    assert ods_first_sheet_row_count(SINGLE) == 1


def test_first_sheet_row_count_returns_int():
    assert isinstance(ods_first_sheet_row_count(MINIMAL), int)


# --- ods_all_sheets_named ---

def test_all_sheets_named_minimal():
    assert ods_all_sheets_named(MINIMAL) is True


def test_all_sheets_named_numeric():
    assert ods_all_sheets_named(NUMERIC) is True


def test_all_sheets_named_returns_bool():
    assert isinstance(ods_all_sheets_named(MINIMAL), bool)


# --- ods_has_uniform_sheet_row_count ---

def test_has_uniform_sheet_row_count_minimal():
    assert ods_has_uniform_sheet_row_count(MINIMAL) is True


def test_has_uniform_sheet_row_count_numeric():
    assert ods_has_uniform_sheet_row_count(NUMERIC) is True


def test_has_uniform_sheet_row_count_single():
    assert ods_has_uniform_sheet_row_count(SINGLE) is True


def test_has_uniform_sheet_row_count_returns_bool():
    assert isinstance(ods_has_uniform_sheet_row_count(MINIMAL), bool)


# --- ods_min_sheet_row_count ---

def test_min_sheet_row_count_minimal():
    assert ods_min_sheet_row_count(MINIMAL) == 2


def test_min_sheet_row_count_numeric():
    assert ods_min_sheet_row_count(NUMERIC) == 1


def test_min_sheet_row_count_single():
    assert ods_min_sheet_row_count(SINGLE) == 1


def test_min_sheet_row_count_returns_int():
    assert isinstance(ods_min_sheet_row_count(MINIMAL), int)
