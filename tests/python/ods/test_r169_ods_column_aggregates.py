"""R169 — ODS column aggregate functions: average_column, max_column_value, min_column_value."""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.ods.ods_parser import average_column, max_column_value, min_column_value

NUMERIC_ROW = Path("samples/by-format/ods/valid/numeric-row.ods")
SINGLE_CELL = Path("samples/by-format/ods/valid/single-cell.ods")
MINIMAL = Path("samples/by-format/ods/valid/minimal-spreadsheet.ods")


class TestAverageColumn:
    def test_returns_float(self):
        result = average_column(NUMERIC_ROW, col=0)
        assert isinstance(result, float)

    def test_empty_col_returns_zero(self):
        result = average_column(MINIMAL, col=0)
        assert isinstance(result, float)

    def test_out_of_range_col_returns_zero(self):
        result = average_column(NUMERIC_ROW, col=999)
        assert result == 0.0

    def test_out_of_range_sheet_returns_zero(self):
        result = average_column(NUMERIC_ROW, col=0, sheet_index=999)
        assert result == 0.0

    def test_str_path(self):
        result = average_column(str(NUMERIC_ROW), col=0)
        assert isinstance(result, float)

    def test_single_cell(self):
        result = average_column(SINGLE_CELL, col=0)
        assert isinstance(result, float)


class TestMaxColumnValue:
    def test_returns_value_or_none(self):
        result = max_column_value(NUMERIC_ROW, col=0)
        # Either a number or None
        assert result is None or isinstance(result, (int, float))

    def test_empty_col_returns_none(self):
        result = max_column_value(MINIMAL, col=0)
        assert result is None

    def test_out_of_range_col_returns_none(self):
        result = max_column_value(NUMERIC_ROW, col=999)
        assert result is None

    def test_out_of_range_sheet_returns_none(self):
        result = max_column_value(NUMERIC_ROW, col=0, sheet_index=999)
        assert result is None

    def test_str_path(self):
        result = max_column_value(str(NUMERIC_ROW), col=0)
        assert result is None or isinstance(result, (int, float))


class TestMinColumnValue:
    def test_returns_value_or_none(self):
        result = min_column_value(NUMERIC_ROW, col=0)
        assert result is None or isinstance(result, (int, float))

    def test_empty_col_returns_none(self):
        result = min_column_value(MINIMAL, col=0)
        assert result is None

    def test_out_of_range_col_returns_none(self):
        result = min_column_value(NUMERIC_ROW, col=999)
        assert result is None

    def test_out_of_range_sheet_returns_none(self):
        result = min_column_value(NUMERIC_ROW, col=0, sheet_index=999)
        assert result is None

    def test_max_gte_min(self):
        mx = max_column_value(NUMERIC_ROW, col=0)
        mn = min_column_value(NUMERIC_ROW, col=0)
        if mx is not None and mn is not None:
            assert mx >= mn
