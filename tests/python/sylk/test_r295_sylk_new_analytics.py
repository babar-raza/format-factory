"""
tests/python/sylk/test_r295_sylk_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-31-20260616
New SYLK analytics: sylk_total_cells, sylk_nonempty_cell_ratio,
                    sylk_min_row_index, sylk_max_row_index, sylk_numeric_cell_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_total_cells,
    sylk_nonempty_cell_ratio,
    sylk_min_row_index,
    sylk_max_row_index,
    sylk_numeric_cell_ratio,
)

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_SYLK_DIR / "minimal-2x2.slk")
_SINGLE = str(_SYLK_DIR / "single-cell.slk")
_NUMERIC = str(_SYLK_DIR / "numeric-row.slk")


class TestSylkTotalCells:
    def test_returns_int(self):
        result = sylk_total_cells(_SINGLE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = sylk_total_cells(path)
            assert result >= 0

    def test_single_cell_is_one(self):
        result = sylk_total_cells(_SINGLE)
        assert result >= 1

    def test_minimal_has_cells(self):
        result = sylk_total_cells(_MINIMAL)
        assert result >= 1


class TestSylkNonemptyCellRatio:
    def test_returns_float(self):
        result = sylk_nonempty_cell_ratio(_SINGLE)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = sylk_nonempty_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_single_cell_nonneg(self):
        result = sylk_nonempty_cell_ratio(_SINGLE)
        assert result >= 0.0

    def test_numeric_row_positive(self):
        result = sylk_nonempty_cell_ratio(_NUMERIC)
        assert result > 0.0


class TestSylkMinRowIndex:
    def test_returns_int(self):
        result = sylk_min_row_index(_SINGLE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = sylk_min_row_index(path)
            assert result >= 0

    def test_leq_max_row_index(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            mn = sylk_min_row_index(path)
            mx = sylk_max_row_index(path)
            assert mn <= mx

    def test_single_cell_positive(self):
        result = sylk_min_row_index(_SINGLE)
        assert result >= 0


class TestSylkMaxRowIndex:
    def test_returns_int(self):
        result = sylk_max_row_index(_SINGLE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = sylk_max_row_index(path)
            assert result >= 0

    def test_geq_min_row_index(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            mn = sylk_min_row_index(path)
            mx = sylk_max_row_index(path)
            assert mx >= mn

    def test_minimal_has_some_rows(self):
        result = sylk_max_row_index(_MINIMAL)
        assert result >= 0


class TestSylkNumericCellRatio:
    def test_returns_float(self):
        result = sylk_numeric_cell_ratio(_NUMERIC)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = sylk_numeric_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_numeric_row_positive(self):
        result = sylk_numeric_cell_ratio(_NUMERIC)
        assert result >= 0.0

    def test_minimal_nonneg(self):
        result = sylk_numeric_cell_ratio(_MINIMAL)
        assert result >= 0.0
