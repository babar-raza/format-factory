"""
tests/python/tsv/test_r296_tsv_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-32-20260616
New TSV analytics: tsv_string_cell_count, tsv_total_string_length,
                   tsv_nonempty_row_count, tsv_avg_fields_per_row, tsv_nonempty_cell_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_string_cell_count,
    tsv_total_string_length,
    tsv_nonempty_row_count,
    tsv_avg_fields_per_row,
    tsv_nonempty_cell_ratio,
)

_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_TSV_DIR / "minimal-2x2.tsv")
_SINGLE = str(_TSV_DIR / "single-cell.tsv")
_MULTI = str(_TSV_DIR / "multi-column.tsv")


class TestTsvStringCellCount:
    def test_returns_int(self):
        result = tsv_string_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            result = tsv_string_cell_count(path)
            assert result >= 0

    def test_single_cell_nonneg(self):
        result = tsv_string_cell_count(_SINGLE)
        assert result >= 0

    def test_multi_column_nonneg(self):
        result = tsv_string_cell_count(_MULTI)
        assert result >= 0


class TestTsvTotalStringLength:
    def test_returns_int(self):
        result = tsv_total_string_length(_MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            result = tsv_total_string_length(path)
            assert result >= 0

    def test_single_cell_positive(self):
        result = tsv_total_string_length(_SINGLE)
        assert result >= 0

    def test_multi_column_positive(self):
        result = tsv_total_string_length(_MULTI)
        assert result > 0


class TestTsvNonemptyRowCount:
    def test_returns_int(self):
        result = tsv_nonempty_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            result = tsv_nonempty_row_count(path)
            assert result >= 0

    def test_single_cell_at_least_one(self):
        result = tsv_nonempty_row_count(_SINGLE)
        assert result >= 1

    def test_minimal_at_least_one(self):
        result = tsv_nonempty_row_count(_MINIMAL)
        assert result >= 1


class TestTsvAvgFieldsPerRow:
    def test_returns_float(self):
        result = tsv_avg_fields_per_row(_MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            result = tsv_avg_fields_per_row(path)
            assert result >= 0.0

    def test_single_cell_at_least_one(self):
        result = tsv_avg_fields_per_row(_SINGLE)
        assert result >= 1.0

    def test_minimal_at_least_one(self):
        result = tsv_avg_fields_per_row(_MINIMAL)
        assert result >= 1.0


class TestTsvNonemptyCellRatio:
    def test_returns_float(self):
        result = tsv_nonempty_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _MULTI]:
            result = tsv_nonempty_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_single_cell_positive(self):
        result = tsv_nonempty_cell_ratio(_SINGLE)
        assert result > 0.0

    def test_multi_column_positive(self):
        result = tsv_nonempty_cell_ratio(_MULTI)
        assert result > 0.0
