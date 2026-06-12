"""Tests for Gnumeric min_column_value and max_column_value functions (rnext35)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import min_column_value, max_column_value


def _model_with_grid(cell_grid: dict) -> dict:
    """Build a minimal Gnumeric model with one sheet."""
    return {"sheets": [{"name": "Sheet1", "cell_grid": cell_grid}]}


class TestMinColumnValue:
    def test_basic_min(self):
        grid = {(0, 0): "10", (1, 0): "3", (2, 0): "7"}
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) == 3.0

    def test_single_value(self):
        grid = {(0, 0): "42"}
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) == 42.0

    def test_no_numeric_returns_none(self):
        grid = {(0, 0): "header", (1, 0): "text"}
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) is None

    def test_empty_column_returns_none(self):
        grid = {(0, 1): "5"}  # col 1, not col 0
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) is None

    def test_negative_values(self):
        grid = {(0, 0): "-5", (1, 0): "-1", (2, 0): "-10"}
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) == -10.0

    def test_mixed_numeric_and_string(self):
        grid = {(0, 0): "header", (1, 0): "5", (2, 0): "2"}
        model = _model_with_grid(grid)
        assert min_column_value(model, 0, 0) == 2.0

    def test_bad_sheet_index(self):
        model = _model_with_grid({})
        with pytest.raises(IndexError):
            min_column_value(model, 5, 0)


class TestMaxColumnValue:
    def test_basic_max(self):
        grid = {(0, 0): "10", (1, 0): "3", (2, 0): "7"}
        model = _model_with_grid(grid)
        assert max_column_value(model, 0, 0) == 10.0

    def test_single_value(self):
        grid = {(0, 0): "99"}
        model = _model_with_grid(grid)
        assert max_column_value(model, 0, 0) == 99.0

    def test_no_numeric_returns_none(self):
        grid = {(0, 0): "header"}
        model = _model_with_grid(grid)
        assert max_column_value(model, 0, 0) is None

    def test_negative_values(self):
        grid = {(0, 0): "-5", (1, 0): "-1", (2, 0): "-10"}
        model = _model_with_grid(grid)
        assert max_column_value(model, 0, 0) == -1.0

    def test_mixed_numeric_and_string(self):
        grid = {(0, 0): "header", (1, 0): "5", (2, 0): "2"}
        model = _model_with_grid(grid)
        assert max_column_value(model, 0, 0) == 5.0
