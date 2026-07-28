"""Tests for extended CSV analytics functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_analytics import (
    csv_max_row_length,
    csv_min_row_length,
    csv_has_uniform_row_length,
    csv_column_count,
    csv_total_cell_count,
    csv_has_header,
)

SAMPLES = Path("samples/by-format/csv")
MINIMAL = SAMPLES / "minimal-2x2.csv"   # headers=[Name,Age], rows=[[Alice,30],[Bob,25]]
QUOTED = SAMPLES / "quoted-fields.csv"
SINGLE = SAMPLES / "single-cell.csv"


# --- csv_max_row_length ---

def test_max_row_length_minimal():
    assert csv_max_row_length(MINIMAL) == 2


def test_max_row_length_single():
    assert csv_max_row_length(SINGLE) >= 1


def test_max_row_length_returns_int():
    assert isinstance(csv_max_row_length(MINIMAL), int)


# --- csv_min_row_length ---

def test_min_row_length_minimal():
    assert csv_min_row_length(MINIMAL) == 2


def test_min_row_length_returns_int():
    assert isinstance(csv_min_row_length(MINIMAL), int)


def test_min_row_length_lte_max():
    assert csv_min_row_length(MINIMAL) <= csv_max_row_length(MINIMAL)


# --- csv_has_uniform_row_length ---

def test_has_uniform_row_length_minimal():
    assert csv_has_uniform_row_length(MINIMAL) is True


def test_has_uniform_row_length_single():
    assert csv_has_uniform_row_length(SINGLE) is True


def test_has_uniform_row_length_returns_bool():
    assert isinstance(csv_has_uniform_row_length(MINIMAL), bool)


# --- csv_column_count ---

def test_column_count_minimal():
    assert csv_column_count(MINIMAL) == 2


def test_column_count_returns_int():
    assert isinstance(csv_column_count(MINIMAL), int)


def test_column_count_positive():
    assert csv_column_count(MINIMAL) > 0


# --- csv_total_cell_count ---

def test_total_cell_count_minimal():
    # 2 data rows x 2 columns = 4
    assert csv_total_cell_count(MINIMAL) == 4


def test_total_cell_count_returns_int():
    assert isinstance(csv_total_cell_count(MINIMAL), int)


def test_total_cell_count_nonnegative():
    assert csv_total_cell_count(MINIMAL) >= 0


def test_total_cell_count_single():
    assert csv_total_cell_count(SINGLE) >= 0


# --- csv_has_header ---

def test_has_header_minimal():
    assert csv_has_header(MINIMAL) is True


def test_has_header_returns_bool():
    assert isinstance(csv_has_header(MINIMAL), bool)


def test_has_header_single():
    # single-cell.csv may or may not have header — just verify it returns bool
    result = csv_has_header(SINGLE)
    assert isinstance(result, bool)
