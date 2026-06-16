"""Tests for 5 new Gnumeric analytics functions.

Uses real sample files from samples/by-format/gnumeric/.
Covers: gnumeric_avg_numeric_value, gnumeric_nonempty_row_ratio,
    gnumeric_longest_row_index, gnumeric_numeric_sum_all, gnumeric_empty_column_count.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_avg_numeric_value,
    gnumeric_nonempty_row_ratio,
    gnumeric_longest_row_index,
    gnumeric_numeric_sum_all,
    gnumeric_empty_column_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = _SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = _SAMPLES / "multi-cell-basic.gnumeric"
EMPTY = _SAMPLES / "empty-sheet.gnumeric"


class TestGnumericAvgNumericValue:
    def test_returns_float(self):
        result = gnumeric_avg_numeric_value(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = gnumeric_avg_numeric_value(MINIMAL)
        assert result >= 0.0

    def test_multi_cell(self):
        result = gnumeric_avg_numeric_value(MULTI)
        assert isinstance(result, float)

    def test_empty_sheet(self):
        result = gnumeric_avg_numeric_value(EMPTY)
        assert result == 0.0


class TestGnumericNonemptyRowRatio:
    def test_returns_float(self):
        result = gnumeric_nonempty_row_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = gnumeric_nonempty_row_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_multi_cell(self):
        result = gnumeric_nonempty_row_ratio(MULTI)
        assert 0.0 <= result <= 1.0

    def test_empty_sheet(self):
        result = gnumeric_nonempty_row_ratio(EMPTY)
        assert result == 0.0


class TestGnumericLongestRowIndex:
    def test_returns_int(self):
        result = gnumeric_longest_row_index(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        result = gnumeric_longest_row_index(MINIMAL)
        assert result >= 0

    def test_multi_cell(self):
        result = gnumeric_longest_row_index(MULTI)
        assert result >= 0

    def test_empty_returns_minus_one(self):
        result = gnumeric_longest_row_index(EMPTY)
        assert result == -1


class TestGnumericNumericSumAll:
    def test_returns_float(self):
        result = gnumeric_numeric_sum_all(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = gnumeric_numeric_sum_all(MINIMAL)
        assert result >= 0.0

    def test_multi_cell(self):
        result = gnumeric_numeric_sum_all(MULTI)
        assert isinstance(result, float)

    def test_empty_zero(self):
        result = gnumeric_numeric_sum_all(EMPTY)
        assert result == 0.0


class TestGnumericEmptyColumnCount:
    def test_returns_int(self):
        result = gnumeric_empty_column_count(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        result = gnumeric_empty_column_count(MINIMAL)
        assert result >= 0

    def test_multi_cell(self):
        result = gnumeric_empty_column_count(MULTI)
        assert isinstance(result, int)

    def test_empty_zero(self):
        result = gnumeric_empty_column_count(EMPTY)
        assert result == 0
