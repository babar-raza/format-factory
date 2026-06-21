"""
Sprint 99 — TSV analytics round 4.
25 tests for 5 new analytics functions:
  tsv_total_field_count, tsv_numeric_field_ratio, tsv_max_field_value_length,
  tsv_nonempty_field_count, tsv_row_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv import (
    tsv_total_field_count,
    tsv_numeric_field_ratio,
    tsv_max_field_value_length,
    tsv_nonempty_field_count,
    tsv_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.tsv")
_SINGLE = str(_SAMPLES / "single-cell.tsv")
_MULTI = str(_SAMPLES / "multi-column.tsv")


# --- tsv_total_field_count ---

class TestTsvTotalFieldCount:
    def test_returns_int(self):
        result = tsv_total_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_total_field_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = tsv_total_field_count(_MINIMAL)
        assert result > 0

    def test_single_cell_gte_one(self):
        result = tsv_total_field_count(_SINGLE)
        assert result >= 1

    def test_multi_column_positive(self):
        result = tsv_total_field_count(_MULTI)
        assert result > 0


# --- tsv_numeric_field_ratio ---

class TestTsvNumericFieldRatio:
    def test_returns_float(self):
        result = tsv_numeric_field_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = tsv_numeric_field_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_single_cell_bounded(self):
        result = tsv_numeric_field_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_multi_column_bounded(self):
        result = tsv_numeric_field_ratio(_MULTI)
        assert 0.0 <= result <= 1.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            r = tsv_numeric_field_ratio(path)
            assert 0.0 <= r <= 1.0


# --- tsv_max_field_value_length ---

class TestTsvMaxFieldValueLength:
    def test_returns_int(self):
        result = tsv_max_field_value_length(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_max_field_value_length(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = tsv_max_field_value_length(_MINIMAL)
        assert result > 0

    def test_single_cell_non_negative(self):
        result = tsv_max_field_value_length(_SINGLE)
        assert result >= 0

    def test_multi_column_positive(self):
        result = tsv_max_field_value_length(_MULTI)
        assert result > 0


# --- tsv_nonempty_field_count ---

class TestTsvNonemptyFieldCount:
    def test_returns_int(self):
        result = tsv_nonempty_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_nonempty_field_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = tsv_nonempty_field_count(_MINIMAL)
        assert result > 0

    def test_single_cell_gte_one(self):
        result = tsv_nonempty_field_count(_SINGLE)
        assert result >= 1

    def test_lte_total_field_count(self):
        nonempty = tsv_nonempty_field_count(_MULTI)
        total = tsv_total_field_count(_MULTI)
        assert nonempty <= total


# --- tsv_row_count ---

class TestTsvRowCount:
    def test_returns_int(self):
        result = tsv_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_row_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = tsv_row_count(_MINIMAL)
        assert result > 0

    def test_single_cell_gte_one(self):
        result = tsv_row_count(_SINGLE)
        assert result >= 1

    def test_multi_column_positive(self):
        result = tsv_row_count(_MULTI)
        assert result > 0
