"""Tests for ODS file-path based analytics in ods_stats.py (extension functions)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_stats import (
    ods_has_data,
    ods_first_sheet_name,
    ods_total_row_count,
    ods_unique_sheet_names,
    ods_has_float_cells,
    ods_max_sheet_row_count,
)

SAMPLES = Path("samples/by-format/ods/valid")
MINIMAL = SAMPLES / "minimal-spreadsheet.ods"   # Sheet1, 2 rows, Name/Value + Alpha/42.0
NUMERIC = SAMPLES / "numeric-row.ods"            # Sheet1, 1 row, 3 float cells
SINGLE  = SAMPLES / "single-cell.ods"            # Sheet1, 1 row, 1 string cell


# --- ods_has_data ---

def test_has_data_minimal():
    assert ods_has_data(MINIMAL) is True


def test_has_data_numeric():
    assert ods_has_data(NUMERIC) is True


def test_has_data_single():
    assert ods_has_data(SINGLE) is True


def test_has_data_returns_bool():
    assert isinstance(ods_has_data(MINIMAL), bool)


# --- ods_first_sheet_name ---

def test_first_sheet_name_minimal():
    assert ods_first_sheet_name(MINIMAL) == "Sheet1"


def test_first_sheet_name_numeric():
    assert ods_first_sheet_name(NUMERIC) == "Sheet1"


def test_first_sheet_name_single():
    assert ods_first_sheet_name(SINGLE) == "Sheet1"


def test_first_sheet_name_returns_str():
    assert isinstance(ods_first_sheet_name(MINIMAL), str)


# --- ods_total_row_count ---

def test_total_row_count_minimal():
    assert ods_total_row_count(MINIMAL) == 2


def test_total_row_count_numeric():
    assert ods_total_row_count(NUMERIC) == 1


def test_total_row_count_single():
    assert ods_total_row_count(SINGLE) == 1


def test_total_row_count_returns_int():
    assert isinstance(ods_total_row_count(MINIMAL), int)


def test_total_row_count_positive():
    assert ods_total_row_count(MINIMAL) > 0


# --- ods_unique_sheet_names ---

def test_unique_sheet_names_minimal():
    assert ods_unique_sheet_names(MINIMAL) == ["Sheet1"]


def test_unique_sheet_names_numeric():
    assert ods_unique_sheet_names(NUMERIC) == ["Sheet1"]


def test_unique_sheet_names_returns_list():
    assert isinstance(ods_unique_sheet_names(MINIMAL), list)


def test_unique_sheet_names_single():
    names = ods_unique_sheet_names(SINGLE)
    assert len(names) == 1


# --- ods_has_float_cells ---

def test_has_float_cells_minimal():
    # minimal has 42.0 (float cell)
    assert ods_has_float_cells(MINIMAL) is True


def test_has_float_cells_numeric():
    assert ods_has_float_cells(NUMERIC) is True


def test_has_float_cells_single():
    # single cell is a string
    assert ods_has_float_cells(SINGLE) is False


def test_has_float_cells_returns_bool():
    assert isinstance(ods_has_float_cells(MINIMAL), bool)


# --- ods_max_sheet_row_count ---

def test_max_sheet_row_count_minimal():
    assert ods_max_sheet_row_count(MINIMAL) == 2


def test_max_sheet_row_count_numeric():
    assert ods_max_sheet_row_count(NUMERIC) == 1


def test_max_sheet_row_count_single():
    assert ods_max_sheet_row_count(SINGLE) == 1


def test_max_sheet_row_count_returns_int():
    assert isinstance(ods_max_sheet_row_count(MINIMAL), int)
