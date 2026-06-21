"""
Sprint r307: Tests for gnumeric_col_span and gnumeric_cells_exceed_rows.
12 tests total (6 per function).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import gnumeric_col_span, gnumeric_cells_exceed_rows

_G = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = _G / "minimal-spreadsheet.gnumeric"
_MULTI = _G / "multi-cell-basic.gnumeric"
_EMPTY = _G / "empty-sheet.gnumeric"


# --- gnumeric_col_span ---

def test_col_span_minimal_returns_int():
    assert isinstance(gnumeric_col_span(_MINIMAL), int)

def test_col_span_minimal_is_1():
    assert gnumeric_col_span(_MINIMAL) == 1

def test_col_span_multi_is_2():
    assert gnumeric_col_span(_MULTI) == 2

def test_col_span_empty_is_0():
    assert gnumeric_col_span(_EMPTY) == 0

def test_col_span_multi_greater_than_minimal():
    assert gnumeric_col_span(_MULTI) > gnumeric_col_span(_MINIMAL)

def test_col_span_empty_is_minimum():
    assert gnumeric_col_span(_EMPTY) == 0


# --- gnumeric_cells_exceed_rows ---

def test_cells_exceed_rows_minimal_returns_bool():
    assert isinstance(gnumeric_cells_exceed_rows(_MINIMAL), bool)

def test_cells_exceed_rows_minimal_is_false():
    # minimal: 1 cell, 1 row — equal, so False
    assert gnumeric_cells_exceed_rows(_MINIMAL) is False

def test_cells_exceed_rows_multi_is_true():
    # multi: 4 cells, 2 rows — exceeds
    assert gnumeric_cells_exceed_rows(_MULTI) is True

def test_cells_exceed_rows_empty_is_false():
    # empty: 0 cells, 0 rows — equal (not strictly greater), so False
    assert gnumeric_cells_exceed_rows(_EMPTY) is False

def test_cells_exceed_rows_only_multi_is_true():
    results = [gnumeric_cells_exceed_rows(p) for p in [_MINIMAL, _MULTI, _EMPTY]]
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_cells_exceed_rows_multi_consistent_with_col_span():
    # multi has more cols than minimal, and also exceeds rows
    assert gnumeric_col_span(_MULTI) > gnumeric_col_span(_MINIMAL)
    assert gnumeric_cells_exceed_rows(_MULTI) is True
