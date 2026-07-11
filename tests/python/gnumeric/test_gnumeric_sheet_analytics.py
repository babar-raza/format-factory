"""Tests for Gnumeric sheet analytics module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_sheet_analytics import (
    gnumeric_has_single_sheet,
    gnumeric_sheet_names_list,
    gnumeric_is_empty_workbook,
    gnumeric_sheets_with_data_count,
    gnumeric_total_unique_value_count,
    gnumeric_has_numeric_values,
)

SAMPLES = Path("samples/by-format/gnumeric")
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"   # 1 cell: 'Hello'
MULTI = SAMPLES / "multi-cell-basic.gnumeric"         # 4 cells: Name, Score, Alice, 42
EMPTY = SAMPLES / "empty-sheet.gnumeric"              # 0 cells


# --- gnumeric_has_single_sheet ---

def test_has_single_sheet_minimal():
    assert gnumeric_has_single_sheet(MINIMAL) is True


def test_has_single_sheet_multi():
    assert gnumeric_has_single_sheet(MULTI) is True


def test_has_single_sheet_empty():
    assert gnumeric_has_single_sheet(EMPTY) is True


def test_has_single_sheet_returns_bool():
    assert isinstance(gnumeric_has_single_sheet(MINIMAL), bool)


# --- gnumeric_sheet_names_list ---

def test_sheet_names_list_minimal():
    assert gnumeric_sheet_names_list(MINIMAL) == ["Sheet1"]


def test_sheet_names_list_multi():
    assert gnumeric_sheet_names_list(MULTI) == ["Sheet1"]


def test_sheet_names_list_empty():
    assert gnumeric_sheet_names_list(EMPTY) == ["Empty"]


def test_sheet_names_list_returns_list():
    assert isinstance(gnumeric_sheet_names_list(MINIMAL), list)


# --- gnumeric_is_empty_workbook ---

def test_is_empty_workbook_minimal():
    assert gnumeric_is_empty_workbook(MINIMAL) is False


def test_is_empty_workbook_multi():
    assert gnumeric_is_empty_workbook(MULTI) is False


def test_is_empty_workbook_empty():
    assert gnumeric_is_empty_workbook(EMPTY) is True


def test_is_empty_workbook_returns_bool():
    assert isinstance(gnumeric_is_empty_workbook(MINIMAL), bool)


# --- gnumeric_sheets_with_data_count ---

def test_sheets_with_data_count_minimal():
    assert gnumeric_sheets_with_data_count(MINIMAL) == 1


def test_sheets_with_data_count_multi():
    assert gnumeric_sheets_with_data_count(MULTI) == 1


def test_sheets_with_data_count_empty():
    assert gnumeric_sheets_with_data_count(EMPTY) == 0


def test_sheets_with_data_count_returns_int():
    assert isinstance(gnumeric_sheets_with_data_count(MINIMAL), int)


# --- gnumeric_total_unique_value_count ---

def test_total_unique_value_count_minimal():
    assert gnumeric_total_unique_value_count(MINIMAL) == 1  # 'Hello'


def test_total_unique_value_count_multi():
    # 'Name', 'Score', 'Alice', '42' — all distinct
    assert gnumeric_total_unique_value_count(MULTI) == 4


def test_total_unique_value_count_empty():
    assert gnumeric_total_unique_value_count(EMPTY) == 0


def test_total_unique_value_count_returns_int():
    assert isinstance(gnumeric_total_unique_value_count(MINIMAL), int)


# --- gnumeric_has_numeric_values ---

def test_has_numeric_values_multi():
    assert gnumeric_has_numeric_values(MULTI) is True  # '42' is numeric


def test_has_numeric_values_minimal():
    assert gnumeric_has_numeric_values(MINIMAL) is False  # 'Hello' is not numeric


def test_has_numeric_values_empty():
    assert gnumeric_has_numeric_values(EMPTY) is False


def test_has_numeric_values_returns_bool():
    assert isinstance(gnumeric_has_numeric_values(MULTI), bool)
