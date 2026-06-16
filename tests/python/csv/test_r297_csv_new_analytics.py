"""
tests/python/csv/test_r297_csv_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-33-20260616
New CSV analytics: csv_string_cell_count, csv_nonempty_row_count,
                   csv_avg_fields_per_row, csv_nonempty_cell_ratio, csv_numeric_cell_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_string_cell_count,
    csv_nonempty_row_count,
    csv_avg_fields_per_row,
    csv_nonempty_cell_ratio,
    csv_numeric_cell_ratio,
)

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_CSV_DIR / "minimal-2x2.csv")
_SINGLE = str(_CSV_DIR / "single-cell.csv")
_QUOTED = str(_CSV_DIR / "quoted-fields.csv")


class TestCsvStringCellCount:
    def test_returns_int(self):
        result = csv_string_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            result = csv_string_cell_count(path)
            assert result >= 0

    def test_single_cell_nonneg(self):
        result = csv_string_cell_count(_SINGLE)
        assert result >= 0

    def test_quoted_nonneg(self):
        result = csv_string_cell_count(_QUOTED)
        assert result >= 0


class TestCsvNonemptyRowCount:
    def test_returns_int(self):
        result = csv_nonempty_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            result = csv_nonempty_row_count(path)
            assert result >= 0

    def test_single_cell_at_least_one(self):
        result = csv_nonempty_row_count(_SINGLE)
        assert result >= 1

    def test_minimal_at_least_one(self):
        result = csv_nonempty_row_count(_MINIMAL)
        assert result >= 1


class TestCsvAvgFieldsPerRow:
    def test_returns_float(self):
        result = csv_avg_fields_per_row(_MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            result = csv_avg_fields_per_row(path)
            assert result >= 0.0

    def test_single_cell_at_least_one(self):
        result = csv_avg_fields_per_row(_SINGLE)
        assert result >= 1.0

    def test_minimal_at_least_one(self):
        result = csv_avg_fields_per_row(_MINIMAL)
        assert result >= 1.0


class TestCsvNonemptyCellRatio:
    def test_returns_float(self):
        result = csv_nonempty_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            result = csv_nonempty_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_single_cell_positive(self):
        result = csv_nonempty_cell_ratio(_SINGLE)
        assert result > 0.0

    def test_minimal_positive(self):
        result = csv_nonempty_cell_ratio(_MINIMAL)
        assert result > 0.0


class TestCsvNumericCellRatio:
    def test_returns_float(self):
        result = csv_numeric_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            result = csv_numeric_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_minimal_nonneg(self):
        result = csv_numeric_cell_ratio(_MINIMAL)
        assert result >= 0.0

    def test_quoted_nonneg(self):
        result = csv_numeric_cell_ratio(_QUOTED)
        assert result >= 0.0
