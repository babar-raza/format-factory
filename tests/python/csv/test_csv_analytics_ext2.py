"""Tests for CSV analytics extension functions (second batch)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_analytics import (
    csv_header_names,
    csv_first_row_values,
    csv_last_row_values,
    csv_has_duplicate_headers,
    csv_all_headers_nonempty,
    csv_is_wide,
)

SAMPLES = Path("samples/by-format/csv")
MINIMAL = SAMPLES / "minimal-2x2.csv"
QUOTED = SAMPLES / "quoted-fields.csv"
SINGLE = SAMPLES / "single-cell.csv"
# minimal-2x2.csv: headers=['Name','Age'], rows=[['Alice','30'],['Bob','25']]
# quoted-fields.csv: headers=['name','description','price'], 2 data rows, 3 cols
# single-cell.csv: headers=['value'], rows=[['42']]


# --- csv_header_names ---

def test_header_names_minimal():
    assert csv_header_names(MINIMAL) == ["Name", "Age"]


def test_header_names_quoted():
    assert csv_header_names(QUOTED) == ["name", "description", "price"]


def test_header_names_single():
    assert csv_header_names(SINGLE) == ["value"]


def test_header_names_returns_list():
    assert isinstance(csv_header_names(MINIMAL), list)


# --- csv_first_row_values ---

def test_first_row_values_minimal():
    assert csv_first_row_values(MINIMAL) == ["Alice", "30"]


def test_first_row_values_quoted():
    assert csv_first_row_values(QUOTED) == ["Widget A", "A simple widget, small", "9.99"]


def test_first_row_values_single():
    assert csv_first_row_values(SINGLE) == ["42"]


def test_first_row_values_returns_list():
    assert isinstance(csv_first_row_values(MINIMAL), list)


# --- csv_last_row_values ---

def test_last_row_values_minimal():
    assert csv_last_row_values(MINIMAL) == ["Bob", "25"]


def test_last_row_values_quoted():
    assert csv_last_row_values(QUOTED) == ["Widget B", "A fancy widget", "19.99"]


def test_last_row_values_single():
    assert csv_last_row_values(SINGLE) == ["42"]


def test_last_row_values_returns_list():
    assert isinstance(csv_last_row_values(MINIMAL), list)


# --- csv_has_duplicate_headers ---

def test_has_duplicate_headers_minimal():
    assert csv_has_duplicate_headers(MINIMAL) is False


def test_has_duplicate_headers_quoted():
    assert csv_has_duplicate_headers(QUOTED) is False


def test_has_duplicate_headers_returns_bool():
    assert isinstance(csv_has_duplicate_headers(MINIMAL), bool)


# --- csv_all_headers_nonempty ---

def test_all_headers_nonempty_minimal():
    assert csv_all_headers_nonempty(MINIMAL) is True


def test_all_headers_nonempty_quoted():
    assert csv_all_headers_nonempty(QUOTED) is True


def test_all_headers_nonempty_single():
    assert csv_all_headers_nonempty(SINGLE) is True


def test_all_headers_nonempty_returns_bool():
    assert isinstance(csv_all_headers_nonempty(MINIMAL), bool)


# --- csv_is_wide ---

def test_is_wide_quoted():
    assert csv_is_wide(QUOTED) is True


def test_is_wide_minimal():
    assert csv_is_wide(MINIMAL) is False


def test_is_wide_single():
    assert csv_is_wide(SINGLE) is False


def test_is_wide_returns_bool():
    assert isinstance(csv_is_wide(MINIMAL), bool)
