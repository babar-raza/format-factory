"""Tests for Gnumeric gap closure (Sprint 40).

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_ROW-001  (Gnumeric Row Count Variance)
  GAP-Gnumeric-FOSS-GNUMERIC_SHE-001  (Gnumeric Sheet Name Lengths)
  GAP-Gnumeric-FOSS-GNUMERIC_LON-001  (Gnumeric Longest Row Index)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_longest_row_index,
    gnumeric_row_count_variance,
    gnumeric_sheet_name_lengths,
)

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")


class TestGnumericRowCountVariance:
    def test_return_type(self):
        assert isinstance(gnumeric_row_count_variance(_EMPTY), float)

    def test_zero_for_single_sheet_empty(self):
        # single sheet -> variance across sheets = 0
        assert gnumeric_row_count_variance(_EMPTY) == 0.0

    def test_zero_for_minimal_single_sheet(self):
        assert gnumeric_row_count_variance(_MINIMAL) == 0.0

    def test_zero_for_multi_cell_single_sheet(self):
        assert gnumeric_row_count_variance(_MULTI) == 0.0

    def test_nonnegative(self):
        assert gnumeric_row_count_variance(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert gnumeric_row_count_variance(_MINIMAL) == gnumeric_row_count_variance(_MINIMAL)


class TestGnumericSheetNameLengths:
    def test_return_type(self):
        result = gnumeric_sheet_name_lengths(_EMPTY)
        assert isinstance(result, list)

    def test_exact_value_for_empty_sheet(self):
        # "Sheet" = 5 chars
        assert gnumeric_sheet_name_lengths(_EMPTY) == [5]

    def test_exact_value_for_minimal(self):
        # "Sheet1" = 6 chars
        assert gnumeric_sheet_name_lengths(_MINIMAL) == [6]

    def test_exact_value_for_multi_cell(self):
        assert gnumeric_sheet_name_lengths(_MULTI) == [6]

    def test_all_positive(self):
        lengths = gnumeric_sheet_name_lengths(_MINIMAL)
        assert all(n >= 1 for n in lengths)

    def test_consistent_across_calls(self):
        assert gnumeric_sheet_name_lengths(_MINIMAL) == gnumeric_sheet_name_lengths(_MINIMAL)


class TestGnumericLongestRowIndex:
    def test_return_type(self):
        assert isinstance(gnumeric_longest_row_index(_EMPTY), int)

    def test_minus_1_for_empty_sheet(self):
        # no rows -> -1
        assert gnumeric_longest_row_index(_EMPTY) == -1

    def test_zero_for_minimal(self):
        assert gnumeric_longest_row_index(_MINIMAL) == 0

    def test_zero_for_multi_cell(self):
        assert gnumeric_longest_row_index(_MULTI) == 0

    def test_consistent_across_calls(self):
        assert gnumeric_longest_row_index(_MINIMAL) == gnumeric_longest_row_index(_MINIMAL)
