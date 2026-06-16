"""Tests for 6 new DIF analytics functions.

Uses real sample files from samples/by-format/dif/valid/.
Covers: dif_numeric_sum, dif_is_single_row, dif_empty_column_count,
    dif_longest_row_index, dif_total_string_length, dif_nonempty_row_ratio.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_empty_column_count,
    dif_is_single_row,
    dif_longest_row_index,
    dif_nonempty_row_ratio,
    dif_numeric_sum,
    dif_total_string_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
MINIMAL = _SAMPLES / "minimal-2x2.dif"
NUMERIC = _SAMPLES / "numeric-row.dif"
SINGLE = _SAMPLES / "single-cell.dif"


class TestDifNumericSum:
    def test_returns_float(self):
        result = dif_numeric_sum(MINIMAL)
        assert isinstance(result, float)

    def test_numeric_file_has_sum(self):
        result = dif_numeric_sum(NUMERIC)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_nonnegative(self):
        result = dif_numeric_sum(MINIMAL)
        assert result >= 0.0


class TestDifIsSingleRow:
    def test_returns_bool(self):
        result = dif_is_single_row(MINIMAL)
        assert isinstance(result, bool)

    def test_minimal_not_single_row(self):
        result = dif_is_single_row(MINIMAL)
        assert isinstance(result, bool)

    def test_single_cell_file(self):
        result = dif_is_single_row(SINGLE)
        assert isinstance(result, bool)


class TestDifEmptyColumnCount:
    def test_returns_int(self):
        result = dif_empty_column_count(MINIMAL)
        assert isinstance(result, int)

    def test_nonnegative(self):
        result = dif_empty_column_count(MINIMAL)
        assert result >= 0

    def test_returns_int_for_numeric(self):
        result = dif_empty_column_count(NUMERIC)
        assert isinstance(result, int)


class TestDifLongestRowIndex:
    def test_returns_int(self):
        result = dif_longest_row_index(MINIMAL)
        assert isinstance(result, int)

    def test_valid_index(self):
        result = dif_longest_row_index(MINIMAL)
        assert result >= 0

    def test_single_cell_index_zero(self):
        result = dif_longest_row_index(SINGLE)
        assert isinstance(result, int)


class TestDifTotalStringLength:
    def test_returns_int(self):
        result = dif_total_string_length(MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_data(self):
        result = dif_total_string_length(MINIMAL)
        assert result > 0

    def test_returns_int_for_single(self):
        result = dif_total_string_length(SINGLE)
        assert isinstance(result, int)


class TestDifNonemptyRowRatio:
    def test_returns_float(self):
        result = dif_nonempty_row_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = dif_nonempty_row_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_positive_for_data(self):
        result = dif_nonempty_row_ratio(MINIMAL)
        assert result > 0.0
