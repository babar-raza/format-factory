"""Tests for TSV row analytics extension functions (batch 2) in tsv_row_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_row_analytics import (
    tsv_row_count,
    tsv_column_count,
    tsv_has_rows,
    tsv_is_single_row,
    tsv_header_count,
    tsv_has_header,
)

SAMPLES = Path("samples/by-format/tsv")
MINIMAL   = SAMPLES / "minimal-2x2.tsv"      # 2 rows, 2 cols, headers=[Name, Age]
MULTI_COL = SAMPLES / "multi-column.tsv"     # 2 rows, 4 cols, headers=[id,name,score,pass]
SINGLE    = SAMPLES / "single-cell.tsv"      # 1 row, 1 col, headers=[value]


# tsv_row_count
def test_row_count_minimal():
    assert tsv_row_count(MINIMAL) == 2

def test_row_count_multi_col():
    assert tsv_row_count(MULTI_COL) == 2

def test_row_count_single():
    assert tsv_row_count(SINGLE) == 1

def test_row_count_returns_int():
    assert isinstance(tsv_row_count(MINIMAL), int)


# tsv_column_count
def test_column_count_minimal():
    assert tsv_column_count(MINIMAL) == 2

def test_column_count_multi_col():
    assert tsv_column_count(MULTI_COL) == 4

def test_column_count_single():
    assert tsv_column_count(SINGLE) == 1

def test_column_count_returns_int():
    assert isinstance(tsv_column_count(MINIMAL), int)


# tsv_has_rows
def test_has_rows_minimal():
    assert tsv_has_rows(MINIMAL) is True

def test_has_rows_single():
    assert tsv_has_rows(SINGLE) is True

def test_has_rows_returns_bool():
    assert isinstance(tsv_has_rows(MINIMAL), bool)


# tsv_is_single_row
def test_is_single_row_single():
    assert tsv_is_single_row(SINGLE) is True

def test_is_single_row_minimal():
    assert tsv_is_single_row(MINIMAL) is False

def test_is_single_row_returns_bool():
    assert isinstance(tsv_is_single_row(MINIMAL), bool)


# tsv_header_count
def test_header_count_minimal():
    assert tsv_header_count(MINIMAL) == 2

def test_header_count_multi_col():
    assert tsv_header_count(MULTI_COL) == 4

def test_header_count_single():
    assert tsv_header_count(SINGLE) == 1

def test_header_count_returns_int():
    assert isinstance(tsv_header_count(MINIMAL), int)


# tsv_has_header
def test_has_header_minimal():
    assert tsv_has_header(MINIMAL) is True

def test_has_header_multi_col():
    assert tsv_has_header(MULTI_COL) is True

def test_has_header_returns_bool():
    assert isinstance(tsv_has_header(MINIMAL), bool)
