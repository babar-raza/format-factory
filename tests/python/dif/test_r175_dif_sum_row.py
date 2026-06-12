"""Tests for DIF sum_row function (rnext43)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import sum_row

_NUMERIC_ROW = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif")


class TestSumRow:
    def test_numeric_row_from_fixture(self):
        # numeric-row.dif has one row with [1.0, 2.0, 3.0]
        result = sum_row(_NUMERIC_ROW, 0)
        assert abs(result - 6.0) < 1e-9

    def test_out_of_range_returns_zero(self):
        result = sum_row(_NUMERIC_ROW, 99)
        assert result == 0.0

    def test_negative_index_returns_zero(self):
        result = sum_row(_NUMERIC_ROW, -1)
        assert result == 0.0

    def test_returns_float(self):
        result = sum_row(_NUMERIC_ROW, 0)
        assert isinstance(result, float)

    def test_nonexistent_raises(self):
        with pytest.raises(Exception):
            sum_row("/nonexistent/file.dif", 0)
