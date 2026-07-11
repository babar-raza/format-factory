"""Tests for FODS file-path based analytics in fods_file_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.fods_file_analytics import (
    fods_file_sheet_count,
    fods_file_is_fods,
    fods_file_first_sheet_name,
    fods_file_sheet_names,
    fods_file_has_multiple_sheets,
    fods_file_total_rows,
)

SAMPLES = Path("samples/by-format/fods")
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"    # 1 sheet=Sheet1, 1 row
MULTI   = SAMPLES / "multi-sheet-basic.fods"      # 2 sheets=Data+Summary, 3 rows total
TYPED   = SAMPLES / "typed-values-basic.fods"     # 1 sheet=Sheet1, 4 rows


# --- fods_file_sheet_count ---

def test_sheet_count_minimal():
    assert fods_file_sheet_count(MINIMAL) == 1


def test_sheet_count_multi():
    assert fods_file_sheet_count(MULTI) == 2


def test_sheet_count_typed():
    assert fods_file_sheet_count(TYPED) == 1


def test_sheet_count_returns_int():
    assert isinstance(fods_file_sheet_count(MINIMAL), int)


# --- fods_file_is_fods ---

def test_is_fods_minimal():
    assert fods_file_is_fods(MINIMAL) is True


def test_is_fods_multi():
    assert fods_file_is_fods(MULTI) is True


def test_is_fods_returns_bool():
    assert isinstance(fods_file_is_fods(MINIMAL), bool)


# --- fods_file_first_sheet_name ---

def test_first_sheet_name_minimal():
    assert fods_file_first_sheet_name(MINIMAL) == "Sheet1"


def test_first_sheet_name_multi():
    assert fods_file_first_sheet_name(MULTI) == "Data"


def test_first_sheet_name_returns_str():
    assert isinstance(fods_file_first_sheet_name(MINIMAL), str)


# --- fods_file_sheet_names ---

def test_sheet_names_minimal():
    assert fods_file_sheet_names(MINIMAL) == ["Sheet1"]


def test_sheet_names_multi():
    assert fods_file_sheet_names(MULTI) == ["Data", "Summary"]


def test_sheet_names_returns_list():
    assert isinstance(fods_file_sheet_names(MINIMAL), list)


# --- fods_file_has_multiple_sheets ---

def test_has_multiple_sheets_minimal():
    assert fods_file_has_multiple_sheets(MINIMAL) is False


def test_has_multiple_sheets_multi():
    assert fods_file_has_multiple_sheets(MULTI) is True


def test_has_multiple_sheets_returns_bool():
    assert isinstance(fods_file_has_multiple_sheets(MINIMAL), bool)


# --- fods_file_total_rows ---

def test_total_rows_minimal():
    assert fods_file_total_rows(MINIMAL) == 1


def test_total_rows_multi():
    assert fods_file_total_rows(MULTI) == 3


def test_total_rows_typed():
    assert fods_file_total_rows(TYPED) == 4


def test_total_rows_returns_int():
    assert isinstance(fods_file_total_rows(MINIMAL), int)
