"""Tests for TSV row analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_row_analytics import (
    tsv_header_names,
    tsv_first_row_values,
    tsv_last_row_values,
    tsv_has_duplicate_headers,
    tsv_all_headers_nonempty,
    tsv_is_wide,
)

SAMPLES = Path("samples/by-format/tsv")
MINIMAL = SAMPLES / "minimal-2x2.tsv"
MULTI = SAMPLES / "multi-column.tsv"
SINGLE = SAMPLES / "single-cell.tsv"
# minimal-2x2.tsv: headers=['Name','Age'], rows=[['Alice','30'],['Bob','25']]
# multi-column.tsv: headers=['id','name','score','pass'], rows=[['1','Alice','95.5','true'],['2','Bob','82.0','false']]
# single-cell.tsv: headers=['value'], rows=[['42']]


# --- tsv_header_names ---

def test_header_names_minimal():
    assert tsv_header_names(MINIMAL) == ["Name", "Age"]


def test_header_names_multi():
    assert tsv_header_names(MULTI) == ["id", "name", "score", "pass"]


def test_header_names_single():
    assert tsv_header_names(SINGLE) == ["value"]


def test_header_names_returns_list():
    assert isinstance(tsv_header_names(MINIMAL), list)


# --- tsv_first_row_values ---

def test_first_row_values_minimal():
    assert tsv_first_row_values(MINIMAL) == ["Alice", "30"]


def test_first_row_values_multi():
    assert tsv_first_row_values(MULTI) == ["1", "Alice", "95.5", "true"]


def test_first_row_values_single():
    assert tsv_first_row_values(SINGLE) == ["42"]


def test_first_row_values_returns_list():
    assert isinstance(tsv_first_row_values(MINIMAL), list)


# --- tsv_last_row_values ---

def test_last_row_values_minimal():
    assert tsv_last_row_values(MINIMAL) == ["Bob", "25"]


def test_last_row_values_multi():
    assert tsv_last_row_values(MULTI) == ["2", "Bob", "82.0", "false"]


def test_last_row_values_single():
    # single-row file: last == first
    assert tsv_last_row_values(SINGLE) == ["42"]


def test_last_row_values_returns_list():
    assert isinstance(tsv_last_row_values(MINIMAL), list)


# --- tsv_has_duplicate_headers ---

def test_has_duplicate_headers_minimal():
    # 'Name', 'Age' are distinct
    assert tsv_has_duplicate_headers(MINIMAL) is False


def test_has_duplicate_headers_multi():
    assert tsv_has_duplicate_headers(MULTI) is False


def test_has_duplicate_headers_returns_bool():
    assert isinstance(tsv_has_duplicate_headers(MINIMAL), bool)


# --- tsv_all_headers_nonempty ---

def test_all_headers_nonempty_minimal():
    assert tsv_all_headers_nonempty(MINIMAL) is True


def test_all_headers_nonempty_multi():
    assert tsv_all_headers_nonempty(MULTI) is True


def test_all_headers_nonempty_single():
    assert tsv_all_headers_nonempty(SINGLE) is True


def test_all_headers_nonempty_returns_bool():
    assert isinstance(tsv_all_headers_nonempty(MINIMAL), bool)


# --- tsv_is_wide ---

def test_is_wide_multi():
    # 4 columns, 2 rows => wide
    assert tsv_is_wide(MULTI) is True


def test_is_wide_minimal():
    # 2 columns, 2 rows => not wide (equal, not strictly greater)
    assert tsv_is_wide(MINIMAL) is False


def test_is_wide_single():
    # 1 column, 1 row => not wide
    assert tsv_is_wide(SINGLE) is False


def test_is_wide_returns_bool():
    assert isinstance(tsv_is_wide(MINIMAL), bool)
