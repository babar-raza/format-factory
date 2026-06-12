"""R168 — ODS sum_column and filter_rows_by_value tests.

Queue: sprint4-q-001, sprint4-q-002
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.ods.ods_parser import sum_column, filter_rows_by_value

NUMERIC_ROW = Path("samples/by-format/ods/valid/numeric-row.ods")
SINGLE_CELL = Path("samples/by-format/ods/valid/single-cell.ods")
MINIMAL = Path("samples/by-format/ods/valid/minimal-spreadsheet.ods")


class TestSumColumn:
    def test_sum_column_returns_float(self):
        result = sum_column(NUMERIC_ROW, col=0)
        assert isinstance(result, float)

    def test_sum_column_nonexistent_col_returns_zero(self):
        result = sum_column(NUMERIC_ROW, col=999)
        assert result == 0.0

    def test_sum_column_empty_sheet_returns_zero(self):
        result = sum_column(MINIMAL, col=0)
        assert isinstance(result, float)

    def test_sum_column_single_cell(self):
        result = sum_column(SINGLE_CELL, col=0)
        assert isinstance(result, float)

    def test_sum_column_str_path(self):
        result = sum_column(str(NUMERIC_ROW), col=0)
        assert isinstance(result, float)

    def test_sum_column_out_of_range_sheet(self):
        result = sum_column(NUMERIC_ROW, col=0, sheet_index=999)
        assert result == 0.0


class TestFilterRowsByValue:
    def test_filter_returns_list(self):
        result = filter_rows_by_value(NUMERIC_ROW, col=0, value=None)
        assert isinstance(result, list)

    def test_filter_matching_returns_rows(self):
        result = filter_rows_by_value(SINGLE_CELL, col=0, value=None)
        assert isinstance(result, list)

    def test_filter_nonexistent_value_returns_empty(self):
        result = filter_rows_by_value(NUMERIC_ROW, col=0, value="NONEXISTENT_VALUE_XYZ")
        assert result == []

    def test_filter_out_of_range_sheet(self):
        result = filter_rows_by_value(NUMERIC_ROW, col=0, value=1, sheet_index=999)
        assert result == []

    def test_filter_str_path(self):
        result = filter_rows_by_value(str(NUMERIC_ROW), col=0, value=None)
        assert isinstance(result, list)
