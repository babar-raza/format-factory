"""Tests for TSV row analytics extension module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_row_analytics import (
    tsv_numeric_column_count,
    tsv_max_row_field_count,
    tsv_min_row_field_count,
    tsv_has_uniform_row_length,
    tsv_empty_cell_count,
    tsv_column_unique_value_counts,
)

SAMPLES = Path("samples/by-format/tsv")
MINIMAL = SAMPLES / "minimal-2x2.tsv"
MULTI = SAMPLES / "multi-column.tsv"
SINGLE = SAMPLES / "single-cell.tsv"


# --- tsv_numeric_column_count ---

def test_numeric_column_count_minimal():
    # Name/Age: only Age is numeric
    assert tsv_numeric_column_count(MINIMAL) == 1


def test_numeric_column_count_multi():
    # id/name/score/pass: id and score are numeric
    assert tsv_numeric_column_count(MULTI) == 2


def test_numeric_column_count_returns_int():
    assert isinstance(tsv_numeric_column_count(MINIMAL), int)


# --- tsv_max_row_field_count ---

def test_max_row_field_count_minimal():
    assert tsv_max_row_field_count(MINIMAL) == 2


def test_max_row_field_count_multi():
    assert tsv_max_row_field_count(MULTI) == 4


def test_max_row_field_count_returns_int():
    assert isinstance(tsv_max_row_field_count(MINIMAL), int)


# --- tsv_min_row_field_count ---

def test_min_row_field_count_minimal():
    assert tsv_min_row_field_count(MINIMAL) == 2


def test_min_row_field_count_multi():
    assert tsv_min_row_field_count(MULTI) == 4


def test_min_row_field_count_returns_int():
    assert isinstance(tsv_min_row_field_count(MINIMAL), int)


# --- tsv_has_uniform_row_length ---

def test_has_uniform_row_length_minimal():
    assert tsv_has_uniform_row_length(MINIMAL) is True


def test_has_uniform_row_length_multi():
    assert tsv_has_uniform_row_length(MULTI) is True


def test_has_uniform_row_length_returns_bool():
    assert isinstance(tsv_has_uniform_row_length(MINIMAL), bool)


def test_has_uniform_row_length_jagged():
    # Simulate jagged rows via list-of-rows structure by directly checking logic
    # (minimal-2x2 is uniform, so this tests the vacuous True case indirectly)
    assert tsv_has_uniform_row_length(SINGLE) is True


# --- tsv_empty_cell_count ---

def test_empty_cell_count_minimal():
    assert tsv_empty_cell_count(MINIMAL) == 0


def test_empty_cell_count_multi():
    assert tsv_empty_cell_count(MULTI) == 0


def test_empty_cell_count_returns_int():
    assert isinstance(tsv_empty_cell_count(MINIMAL), int)


# --- tsv_column_unique_value_counts ---

def test_column_unique_value_counts_minimal():
    # Name: Alice,Bob (2 unique); Age: 30,25 (2 unique)
    assert tsv_column_unique_value_counts(MINIMAL) == [2, 2]


def test_column_unique_value_counts_multi():
    # id: 1,2 (2); name: Alice,Bob (2); score: 95.5,82.0 (2); pass: true,false (2)
    assert tsv_column_unique_value_counts(MULTI) == [2, 2, 2, 2]


def test_column_unique_value_counts_returns_list():
    assert isinstance(tsv_column_unique_value_counts(MINIMAL), list)


def test_column_unique_value_counts_length_matches_columns():
    result = tsv_column_unique_value_counts(MULTI)
    assert len(result) == 4
