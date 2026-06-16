"""Tests for 5 new SYLK analytics functions.

Uses real sample files from samples/by-format/sylk/valid/.
Covers: sylk_numeric_sum, sylk_avg_numeric_value, sylk_total_string_length,
    sylk_nonempty_row_ratio, sylk_longest_row_index.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk import (
    sylk_avg_numeric_value,
    sylk_longest_row_index,
    sylk_nonempty_row_ratio,
    sylk_numeric_sum,
    sylk_total_string_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
MINIMAL = _SAMPLES / "minimal-2x2.slk"
NUMERIC = _SAMPLES / "numeric-row.slk"
SINGLE = _SAMPLES / "single-cell.slk"


class TestSylkNumericSum:
    def test_returns_float(self):
        result = sylk_numeric_sum(MINIMAL)
        assert isinstance(result, float)

    def test_numeric_file_has_sum(self):
        result = sylk_numeric_sum(NUMERIC)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_nonnegative(self):
        result = sylk_numeric_sum(MINIMAL)
        assert result >= 0.0


class TestSylkAvgNumericValue:
    def test_returns_float(self):
        result = sylk_avg_numeric_value(MINIMAL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = sylk_avg_numeric_value(MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = sylk_avg_numeric_value(NUMERIC)
        assert isinstance(result, float)


class TestSylkTotalStringLength:
    def test_returns_int(self):
        result = sylk_total_string_length(MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_data(self):
        result = sylk_total_string_length(MINIMAL)
        assert result > 0

    def test_single_cell(self):
        result = sylk_total_string_length(SINGLE)
        assert isinstance(result, int)


class TestSylkNonemptyRowRatio:
    def test_returns_float(self):
        result = sylk_nonempty_row_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = sylk_nonempty_row_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_positive_for_data(self):
        result = sylk_nonempty_row_ratio(MINIMAL)
        assert result > 0.0


class TestSylkLongestRowIndex:
    def test_returns_int(self):
        result = sylk_longest_row_index(MINIMAL)
        assert isinstance(result, int)

    def test_positive_row_index(self):
        result = sylk_longest_row_index(MINIMAL)
        assert result >= 1

    def test_single_cell_returns_index(self):
        result = sylk_longest_row_index(SINGLE)
        assert isinstance(result, int)
        assert result >= 1
