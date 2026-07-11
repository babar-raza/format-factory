"""Tests for tsv_row_analytics extension functions (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from tsv.tsv_row_analytics import (
    tsv_first_header,
    tsv_last_header,
    tsv_is_empty,
    tsv_total_cells,
    tsv_is_tall,
    tsv_delimiter,
)

SAMPLES = Path("samples/by-format/tsv")
MINIMAL = SAMPLES / "minimal-2x2.tsv"
MULTI = SAMPLES / "multi-column.tsv"
SINGLE = SAMPLES / "single-cell.tsv"


# --- tsv_first_header ---

def test_first_header_returns_str():
    assert isinstance(tsv_first_header(MINIMAL), str)


def test_first_header_minimal_nonempty():
    assert len(tsv_first_header(MINIMAL)) > 0


# --- tsv_last_header ---

def test_last_header_returns_str():
    assert isinstance(tsv_last_header(MINIMAL), str)


def test_last_header_minimal_nonempty():
    assert len(tsv_last_header(MINIMAL)) > 0


def test_last_header_single_col_equals_first():
    first = tsv_first_header(SINGLE)
    last = tsv_last_header(SINGLE)
    assert first == last  # single column


# --- tsv_is_empty ---

def test_is_empty_minimal_false():
    assert tsv_is_empty(MINIMAL) is False


def test_is_empty_returns_bool():
    assert isinstance(tsv_is_empty(MINIMAL), bool)


# --- tsv_total_cells ---

def test_total_cells_returns_int():
    assert isinstance(tsv_total_cells(MINIMAL), int)


def test_total_cells_minimal_positive():
    assert tsv_total_cells(MINIMAL) > 0


def test_total_cells_minimal_value():
    # minimal-2x2 has 2 rows × 2 columns = 4 cells
    assert tsv_total_cells(MINIMAL) == 4


# --- tsv_is_tall ---

def test_is_tall_returns_bool():
    assert isinstance(tsv_is_tall(MINIMAL), bool)


def test_is_tall_minimal():
    # 2 rows, 2 cols → not tall
    assert tsv_is_tall(MINIMAL) is False


# --- tsv_delimiter ---

def test_delimiter_returns_str():
    assert isinstance(tsv_delimiter(MINIMAL), str)


def test_delimiter_minimal():
    result = tsv_delimiter(MINIMAL)
    assert isinstance(result, str)
