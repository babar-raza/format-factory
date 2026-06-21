"""
test_r336_ods_new_analytics.py
Sprint 72 — 5 new ODS analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import (
    ods_file_size_bytes,
    ods_total_row_count,
    ods_nonempty_sheet_count,
    ods_max_row_count,
    ods_string_cell_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")
_NUMERIC = str(_SAMPLES / "numeric-row.ods")
_SINGLE = str(_SAMPLES / "single-cell.ods")


# --- ods_file_size_bytes ---

class TestOdsFileSizeBytes:
    def test_returns_int(self):
        assert isinstance(ods_file_size_bytes(_MINIMAL), int)

    def test_positive(self):
        assert ods_file_size_bytes(_MINIMAL) > 0

    def test_numeric_positive(self):
        assert ods_file_size_bytes(_NUMERIC) > 0

    def test_single_positive(self):
        assert ods_file_size_bytes(_SINGLE) > 0

    def test_non_negative(self):
        assert ods_file_size_bytes(_MINIMAL) >= 0


# --- ods_total_row_count ---

class TestOdsTotalRowCount:
    def test_returns_int(self):
        assert isinstance(ods_total_row_count(_MINIMAL), int)

    def test_non_negative(self):
        assert ods_total_row_count(_MINIMAL) >= 0

    def test_minimal_has_rows(self):
        assert ods_total_row_count(_MINIMAL) >= 1

    def test_single_non_negative(self):
        assert ods_total_row_count(_SINGLE) >= 0

    def test_numeric_non_negative(self):
        assert ods_total_row_count(_NUMERIC) >= 0


# --- ods_nonempty_sheet_count ---

class TestOdsNonemptySheetCount:
    def test_returns_int(self):
        assert isinstance(ods_nonempty_sheet_count(_MINIMAL), int)

    def test_non_negative(self):
        assert ods_nonempty_sheet_count(_MINIMAL) >= 0

    def test_minimal_has_content(self):
        assert ods_nonempty_sheet_count(_MINIMAL) >= 1

    def test_numeric_non_negative(self):
        assert ods_nonempty_sheet_count(_NUMERIC) >= 0

    def test_single_non_negative(self):
        assert ods_nonempty_sheet_count(_SINGLE) >= 0


# --- ods_max_row_count ---

class TestOdsMaxRowCount:
    def test_returns_int(self):
        assert isinstance(ods_max_row_count(_MINIMAL), int)

    def test_non_negative(self):
        assert ods_max_row_count(_MINIMAL) >= 0

    def test_minimal_has_rows(self):
        assert ods_max_row_count(_MINIMAL) >= 1

    def test_single_has_row(self):
        assert ods_max_row_count(_SINGLE) >= 1

    def test_numeric_has_row(self):
        assert ods_max_row_count(_NUMERIC) >= 1


# --- ods_string_cell_ratio ---

class TestOdsStringCellRatio:
    def test_returns_float(self):
        assert isinstance(ods_string_cell_ratio(_MINIMAL), float)

    def test_non_negative(self):
        assert ods_string_cell_ratio(_MINIMAL) >= 0.0

    def test_between_zero_and_one(self):
        assert 0.0 <= ods_string_cell_ratio(_MINIMAL) <= 1.0

    def test_numeric_between_zero_one(self):
        assert 0.0 <= ods_string_cell_ratio(_NUMERIC) <= 1.0

    def test_single_between_zero_one(self):
        assert 0.0 <= ods_string_cell_ratio(_SINGLE) <= 1.0
