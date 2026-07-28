"""Tests for CSV stats extension functions (batch 2) in csv_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import parse_csv
from src.python.ff_csv.csv_stats import (
    csv_header_count,
    csv_has_headers,
    csv_first_row,
    csv_last_row,
    csv_is_square,
    csv_is_tall,
)

SAMPLES = Path("samples/by-format/csv")
MINIMAL    = SAMPLES / "minimal-2x2.csv"      # 2 rows, 2 cols, headers=[Name,Age]
SINGLE     = SAMPLES / "single-cell.csv"      # 1 row, 1 col, headers=[value]
QUOTED     = SAMPLES / "quoted-fields.csv"    # 2 rows, 3 cols

def _doc(path):
    return parse_csv(path)


# csv_header_count
def test_header_count_minimal():
    assert csv_header_count(_doc(MINIMAL)) == 2

def test_header_count_single():
    assert csv_header_count(_doc(SINGLE)) == 1

def test_header_count_quoted():
    assert csv_header_count(_doc(QUOTED)) == 3

def test_header_count_returns_int():
    assert isinstance(csv_header_count(_doc(MINIMAL)), int)


# csv_has_headers
def test_has_headers_minimal():
    assert csv_has_headers(_doc(MINIMAL)) is True

def test_has_headers_single():
    assert csv_has_headers(_doc(SINGLE)) is True

def test_has_headers_returns_bool():
    assert isinstance(csv_has_headers(_doc(MINIMAL)), bool)


# csv_first_row
def test_first_row_minimal():
    row = csv_first_row(_doc(MINIMAL))
    assert row == ["Alice", "30"]

def test_first_row_single():
    row = csv_first_row(_doc(SINGLE))
    assert row == ["42"]

def test_first_row_returns_list():
    assert isinstance(csv_first_row(_doc(MINIMAL)), list)


# csv_last_row
def test_last_row_minimal():
    row = csv_last_row(_doc(MINIMAL))
    assert row == ["Bob", "25"]

def test_last_row_single():
    row = csv_last_row(_doc(SINGLE))
    assert row == ["42"]

def test_last_row_returns_list():
    assert isinstance(csv_last_row(_doc(MINIMAL)), list)


# csv_is_square
def test_is_square_minimal():
    # 2 rows, 2 cols → square
    assert csv_is_square(_doc(MINIMAL)) is True

def test_is_square_single():
    # 1 row, 1 col → square
    assert csv_is_square(_doc(SINGLE)) is True

def test_is_square_quoted():
    # 2 rows, 3 cols → not square
    assert csv_is_square(_doc(QUOTED)) is False

def test_is_square_returns_bool():
    assert isinstance(csv_is_square(_doc(MINIMAL)), bool)


# csv_is_tall
def test_is_tall_quoted():
    # 2 rows, 3 cols → not tall
    assert csv_is_tall(_doc(QUOTED)) is False

def test_is_tall_minimal():
    # 2 rows, 2 cols → not tall
    assert csv_is_tall(_doc(MINIMAL)) is False

def test_is_tall_returns_bool():
    assert isinstance(csv_is_tall(_doc(MINIMAL)), bool)
