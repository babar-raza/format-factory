"""Tests for 5 new FODS analytics functions.

Uses real sample files from samples/by-format/fods/.
Covers: fods_avg_numeric_value, fods_nonempty_row_ratio, fods_longest_row_index,
    fods_numeric_sum_all, fods_empty_column_count.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods,
    fods_avg_numeric_value,
    fods_nonempty_row_ratio,
    fods_longest_row_index,
    fods_numeric_sum_all,
    fods_empty_column_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
MINIMAL = _SAMPLES / "minimal-spreadsheet.fods"
NUMERIC = _SAMPLES / "typed-values-basic.fods"
MULTI = _SAMPLES / "multi-sheet-basic.fods"


def _load(path):
    return parse_fods(str(path))


class TestFodsAvgNumericValue:
    def test_returns_float(self):
        wb = _load(MINIMAL)
        result = fods_avg_numeric_value(wb)
        assert isinstance(result, float)

    def test_nonneg(self):
        wb = _load(MINIMAL)
        result = fods_avg_numeric_value(wb)
        assert result >= 0.0

    def test_numeric_file(self):
        wb = _load(NUMERIC)
        result = fods_avg_numeric_value(wb)
        assert isinstance(result, float)

    def test_multi_sheet(self):
        wb = _load(MULTI)
        result = fods_avg_numeric_value(wb)
        assert isinstance(result, float)


class TestFodsNonemptyRowRatio:
    def test_returns_float(self):
        wb = _load(MINIMAL)
        result = fods_nonempty_row_ratio(wb)
        assert isinstance(result, float)

    def test_in_range(self):
        wb = _load(MINIMAL)
        result = fods_nonempty_row_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_numeric_file(self):
        wb = _load(NUMERIC)
        result = fods_nonempty_row_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_multi_sheet_default_sheet(self):
        wb = _load(MULTI)
        result = fods_nonempty_row_ratio(wb)
        assert 0.0 <= result <= 1.0


class TestFodsLongestRowIndex:
    def test_returns_int(self):
        wb = _load(MINIMAL)
        result = fods_longest_row_index(wb)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        wb = _load(MINIMAL)
        result = fods_longest_row_index(wb)
        assert result >= 0

    def test_numeric_file(self):
        wb = _load(NUMERIC)
        result = fods_longest_row_index(wb)
        assert result >= 0

    def test_multi_sheet(self):
        wb = _load(MULTI)
        result = fods_longest_row_index(wb)
        assert result >= 0


class TestFodsNumericSumAll:
    def test_returns_float(self):
        wb = _load(MINIMAL)
        result = fods_numeric_sum_all(wb)
        assert isinstance(result, float)

    def test_nonneg(self):
        wb = _load(MINIMAL)
        result = fods_numeric_sum_all(wb)
        assert result >= 0.0

    def test_numeric_file(self):
        wb = _load(NUMERIC)
        result = fods_numeric_sum_all(wb)
        assert isinstance(result, float)

    def test_multi_sheet(self):
        wb = _load(MULTI)
        result = fods_numeric_sum_all(wb)
        assert isinstance(result, float)


class TestFodsEmptyColumnCount:
    def test_returns_int(self):
        wb = _load(MINIMAL)
        result = fods_empty_column_count(wb)
        assert isinstance(result, int)

    def test_nonneg(self):
        wb = _load(MINIMAL)
        result = fods_empty_column_count(wb)
        assert result >= 0

    def test_numeric_file(self):
        wb = _load(NUMERIC)
        result = fods_empty_column_count(wb)
        assert isinstance(result, int)

    def test_multi_sheet(self):
        wb = _load(MULTI)
        result = fods_empty_column_count(wb)
        assert isinstance(result, int)
