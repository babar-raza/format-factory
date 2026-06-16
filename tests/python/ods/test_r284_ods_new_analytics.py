"""Tests for 5 new ODS analytics functions.

Uses real sample files from samples/by-format/ods/valid/.
Covers: ods_avg_numeric_value, ods_nonempty_row_ratio, ods_longest_row_index,
    ods_numeric_sum_all, ods_empty_column_count.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    ods_avg_numeric_value,
    ods_nonempty_row_ratio,
    ods_longest_row_index,
    ods_numeric_sum_all,
    ods_empty_column_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
MINIMAL = _SAMPLES / "minimal-spreadsheet.ods"
NUMERIC = _SAMPLES / "numeric-row.ods"
SINGLE = _SAMPLES / "single-cell.ods"


class TestOdsAvgNumericValue:
    def test_returns_float(self):
        result = ods_avg_numeric_value(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = ods_avg_numeric_value(MINIMAL)
        assert result >= 0.0

    def test_numeric_row_positive(self):
        result = ods_avg_numeric_value(NUMERIC)
        assert result >= 0.0

    def test_single_cell(self):
        result = ods_avg_numeric_value(SINGLE)
        assert isinstance(result, float)


class TestOdsNonemptyRowRatio:
    def test_returns_float(self):
        result = ods_nonempty_row_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = ods_nonempty_row_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_numeric_row(self):
        result = ods_nonempty_row_ratio(NUMERIC)
        assert 0.0 <= result <= 1.0

    def test_single_cell_positive(self):
        result = ods_nonempty_row_ratio(SINGLE)
        assert result > 0.0


class TestOdsLongestRowIndex:
    def test_returns_int(self):
        result = ods_longest_row_index(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        result = ods_longest_row_index(MINIMAL)
        assert result >= 0

    def test_numeric_row(self):
        result = ods_longest_row_index(NUMERIC)
        assert result >= 0

    def test_single_cell(self):
        result = ods_longest_row_index(SINGLE)
        assert result >= 0


class TestOdsNumericSumAll:
    def test_returns_float(self):
        result = ods_numeric_sum_all(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = ods_numeric_sum_all(MINIMAL)
        assert result >= 0.0

    def test_numeric_row(self):
        result = ods_numeric_sum_all(NUMERIC)
        assert isinstance(result, float)

    def test_single_cell(self):
        result = ods_numeric_sum_all(SINGLE)
        assert isinstance(result, float)


class TestOdsEmptyColumnCount:
    def test_returns_int(self):
        result = ods_empty_column_count(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        result = ods_empty_column_count(MINIMAL)
        assert result >= 0

    def test_numeric_row(self):
        result = ods_empty_column_count(NUMERIC)
        assert isinstance(result, int)

    def test_single_cell(self):
        result = ods_empty_column_count(SINGLE)
        assert isinstance(result, int)
