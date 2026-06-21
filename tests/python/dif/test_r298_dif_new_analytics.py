"""
tests/python/dif/test_r298_dif_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-34-20260616
New DIF analytics: dif_numeric_cell_ratio, dif_string_cell_ratio,
                   dif_min_row_index, dif_max_row_index, dif_vectors_tuples_sum
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_numeric_cell_ratio,
    dif_string_cell_ratio,
    dif_min_row_index,
    dif_max_row_index,
    dif_vectors_tuples_sum,
)

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIF_DIR / "minimal-2x2.dif")
_SINGLE = str(_DIF_DIR / "single-cell.dif")
_NUMERIC = str(_DIF_DIR / "numeric-row.dif")


class TestDifNumericCellRatio:
    def test_returns_float(self):
        result = dif_numeric_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = dif_numeric_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_numeric_row_positive(self):
        result = dif_numeric_cell_ratio(_NUMERIC)
        assert result >= 0.0

    def test_minimal_nonneg(self):
        result = dif_numeric_cell_ratio(_MINIMAL)
        assert result >= 0.0


class TestDifStringCellRatio:
    def test_returns_float(self):
        result = dif_string_cell_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = dif_string_cell_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_adds_to_at_most_one_with_numeric(self):
        for path in [_MINIMAL, _NUMERIC]:
            r_str = dif_string_cell_ratio(path)
            r_num = dif_numeric_cell_ratio(path)
            assert r_str + r_num <= 1.0 + 1e-9

    def test_minimal_nonneg(self):
        result = dif_string_cell_ratio(_MINIMAL)
        assert result >= 0.0


class TestDifMinRowIndex:
    def test_returns_int(self):
        result = dif_min_row_index(_SINGLE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = dif_min_row_index(path)
            assert result >= 0

    def test_leq_max_row_index(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            mn = dif_min_row_index(path)
            mx = dif_max_row_index(path)
            assert mn <= mx

    def test_single_cell_nonneg(self):
        result = dif_min_row_index(_SINGLE)
        assert result >= 0


class TestDifMaxRowIndex:
    def test_returns_int(self):
        result = dif_max_row_index(_SINGLE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = dif_max_row_index(path)
            assert result >= 0

    def test_geq_min_row_index(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            mn = dif_min_row_index(path)
            mx = dif_max_row_index(path)
            assert mx >= mn

    def test_minimal_nonneg(self):
        result = dif_max_row_index(_MINIMAL)
        assert result >= 0


class TestDifVectorsTuplesSum:
    def test_returns_int(self):
        result = dif_vectors_tuples_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_positive(self):
        for path in [_MINIMAL, _SINGLE, _NUMERIC]:
            result = dif_vectors_tuples_sum(path)
            assert result > 0

    def test_single_cell_at_least_two(self):
        result = dif_vectors_tuples_sum(_SINGLE)
        assert result >= 2

    def test_minimal_at_least_two(self):
        result = dif_vectors_tuples_sum(_MINIMAL)
        assert result >= 2
