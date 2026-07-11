"""Tests for Gnumeric workbook stats extension functions in gnumeric_workbook_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import load
from src.python.gnumeric.gnumeric_workbook_stats import (
    workbook_sheet_count,
    workbook_total_cell_count,
    workbook_sheet_names,
    workbook_has_data,
    workbook_is_gnumeric,
    workbook_max_sheet_cell_count,
)

SAMPLES = Path("samples/by-format/gnumeric")
EMPTY   = SAMPLES / "empty-sheet.gnumeric"         # 1 sheet 'Empty', 0 cells
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"  # 1 sheet 'Sheet1', 1 cell
MULTI   = SAMPLES / "multi-cell-basic.gnumeric"     # 1 sheet 'Sheet1', 4 cells

def _model(path):
    return load(path)


# workbook_sheet_count
def test_sheet_count_empty():
    assert workbook_sheet_count(_model(EMPTY)) == 1

def test_sheet_count_minimal():
    assert workbook_sheet_count(_model(MINIMAL)) == 1

def test_sheet_count_returns_int():
    assert isinstance(workbook_sheet_count(_model(MINIMAL)), int)


# workbook_total_cell_count
def test_total_cell_count_empty():
    assert workbook_total_cell_count(_model(EMPTY)) == 0

def test_total_cell_count_minimal():
    assert workbook_total_cell_count(_model(MINIMAL)) == 1

def test_total_cell_count_multi():
    assert workbook_total_cell_count(_model(MULTI)) == 4

def test_total_cell_count_returns_int():
    assert isinstance(workbook_total_cell_count(_model(MINIMAL)), int)


# workbook_sheet_names
def test_sheet_names_empty():
    assert workbook_sheet_names(_model(EMPTY)) == ["Empty"]

def test_sheet_names_minimal():
    assert workbook_sheet_names(_model(MINIMAL)) == ["Sheet1"]

def test_sheet_names_returns_list():
    assert isinstance(workbook_sheet_names(_model(MINIMAL)), list)


# workbook_has_data
def test_has_data_empty():
    assert workbook_has_data(_model(EMPTY)) is False

def test_has_data_minimal():
    assert workbook_has_data(_model(MINIMAL)) is True

def test_has_data_returns_bool():
    assert isinstance(workbook_has_data(_model(MINIMAL)), bool)


# workbook_is_gnumeric
def test_is_gnumeric_minimal():
    assert workbook_is_gnumeric(_model(MINIMAL)) is True

def test_is_gnumeric_returns_bool():
    assert isinstance(workbook_is_gnumeric(_model(MINIMAL)), bool)


# workbook_max_sheet_cell_count
def test_max_sheet_cell_count_empty():
    assert workbook_max_sheet_cell_count(_model(EMPTY)) == 0

def test_max_sheet_cell_count_minimal():
    assert workbook_max_sheet_cell_count(_model(MINIMAL)) == 1

def test_max_sheet_cell_count_multi():
    assert workbook_max_sheet_cell_count(_model(MULTI)) == 4

def test_max_sheet_cell_count_returns_int():
    assert isinstance(workbook_max_sheet_cell_count(_model(MINIMAL)), int)
