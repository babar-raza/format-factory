"""Tests for ODS stats extension functions (batch 3) in ods_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_stats import (
    ods_sheet_count,
    ods_has_sheets,
    ods_first_sheet_name,
    ods_has_data,
    ods_max_sheet_name_length,
    ods_last_sheet_name,
)

SAMPLES = Path("samples/by-format/ods/valid")
MINIMAL = SAMPLES / "minimal-spreadsheet.ods"   # 1 sheet 'Sheet1', 2 rows
NUMERIC = SAMPLES / "numeric-row.ods"            # 1 sheet 'Sheet1', 1 row
SINGLE  = SAMPLES / "single-cell.ods"            # 1 sheet 'Sheet1', 1 row


# ods_sheet_count
def test_sheet_count_minimal():
    assert ods_sheet_count(MINIMAL) == 1

def test_sheet_count_returns_int():
    assert isinstance(ods_sheet_count(MINIMAL), int)


# ods_has_sheets
def test_has_sheets_minimal():
    assert ods_has_sheets(MINIMAL) is True

def test_has_sheets_returns_bool():
    assert isinstance(ods_has_sheets(MINIMAL), bool)


# ods_first_sheet_name
def test_first_sheet_name_minimal():
    assert ods_first_sheet_name(MINIMAL) == "Sheet1"

def test_first_sheet_name_numeric():
    assert ods_first_sheet_name(NUMERIC) == "Sheet1"

def test_first_sheet_name_returns_str():
    assert isinstance(ods_first_sheet_name(MINIMAL), str)


# ods_has_data
def test_has_data_minimal():
    assert ods_has_data(MINIMAL) is True

def test_has_data_numeric():
    assert ods_has_data(NUMERIC) is True

def test_has_data_returns_bool():
    assert isinstance(ods_has_data(MINIMAL), bool)


# ods_max_sheet_name_length
def test_max_sheet_name_length_minimal():
    # "Sheet1" = 6 chars
    assert ods_max_sheet_name_length(MINIMAL) == 6

def test_max_sheet_name_length_returns_int():
    assert isinstance(ods_max_sheet_name_length(MINIMAL), int)


# ods_last_sheet_name
def test_last_sheet_name_minimal():
    assert ods_last_sheet_name(MINIMAL) == "Sheet1"

def test_last_sheet_name_single():
    assert ods_last_sheet_name(SINGLE) == "Sheet1"

def test_last_sheet_name_returns_str():
    assert isinstance(ods_last_sheet_name(MINIMAL), str)
