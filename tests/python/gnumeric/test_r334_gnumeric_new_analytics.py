"""
test_r334_gnumeric_new_analytics.py
Sprint 70 — 5 new Gnumeric analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_file_size_bytes,
    gnumeric_unique_sheet_count,
    gnumeric_max_row_index,
    gnumeric_max_col_index,
    gnumeric_formula_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")
_EMPTY = str(_SAMPLES / "empty-sheet.gnumeric")


# --- gnumeric_file_size_bytes ---

class TestGnumericFileSizeBytes:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes(_MINIMAL), int)

    def test_positive(self):
        assert gnumeric_file_size_bytes(_MINIMAL) > 0

    def test_multi_positive(self):
        assert gnumeric_file_size_bytes(_MULTI) > 0

    def test_empty_positive(self):
        assert gnumeric_file_size_bytes(_EMPTY) > 0

    def test_non_negative(self):
        assert gnumeric_file_size_bytes(_MINIMAL) >= 0


# --- gnumeric_unique_sheet_count ---

class TestGnumericUniqueSheetCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_unique_sheet_count(_MINIMAL), int)

    def test_non_negative(self):
        assert gnumeric_unique_sheet_count(_MINIMAL) >= 0

    def test_minimal_has_sheet(self):
        assert gnumeric_unique_sheet_count(_MINIMAL) >= 1

    def test_multi_has_sheet(self):
        assert gnumeric_unique_sheet_count(_MULTI) >= 1

    def test_empty_non_negative(self):
        assert gnumeric_unique_sheet_count(_EMPTY) >= 0


# --- gnumeric_max_row_index ---

class TestGnumericMaxRowIndex:
    def test_returns_int(self):
        assert isinstance(gnumeric_max_row_index(_MINIMAL), int)

    def test_empty_returns_minus_one(self):
        assert gnumeric_max_row_index(_EMPTY) >= -1

    def test_minimal_non_negative(self):
        assert gnumeric_max_row_index(_MINIMAL) >= -1

    def test_multi_non_negative(self):
        assert gnumeric_max_row_index(_MULTI) >= -1

    def test_multi_has_rows(self):
        assert gnumeric_max_row_index(_MULTI) >= 0


# --- gnumeric_max_col_index ---

class TestGnumericMaxColIndex:
    def test_returns_int(self):
        assert isinstance(gnumeric_max_col_index(_MINIMAL), int)

    def test_empty_returns_minus_one(self):
        assert gnumeric_max_col_index(_EMPTY) >= -1

    def test_minimal_non_negative(self):
        assert gnumeric_max_col_index(_MINIMAL) >= -1

    def test_multi_non_negative(self):
        assert gnumeric_max_col_index(_MULTI) >= -1

    def test_multi_has_cols(self):
        assert gnumeric_max_col_index(_MULTI) >= 0


# --- gnumeric_formula_count ---

class TestGnumericFormulaCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_formula_count(_MINIMAL), int)

    def test_non_negative(self):
        assert gnumeric_formula_count(_MINIMAL) >= 0

    def test_multi_non_negative(self):
        assert gnumeric_formula_count(_MULTI) >= 0

    def test_empty_non_negative(self):
        assert gnumeric_formula_count(_EMPTY) >= 0

    def test_returns_int_for_all(self):
        assert isinstance(gnumeric_formula_count(_MULTI), int)
