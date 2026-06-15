"""Tests for gnumeric_empty_cell_count — count empty/None cells in a sheet."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_empty_cell_count,
    gnumeric_numeric_cell_count,
    gnumeric_string_cell_count,
    count_nonempty_cells,
    load,
    create_gnumeric,
)


class TestGnumericEmptyCellCount:
    def test_returns_int(self):
        model = create_gnumeric([{"name": "S1", "rows": [["a", "b"]]}])
        assert isinstance(gnumeric_empty_cell_count(model, 0), int)

    def test_no_empty_cells(self):
        model = create_gnumeric([{"name": "S1", "rows": [["a", "b"], ["1", "2"]]}])
        assert gnumeric_empty_cell_count(model, 0) == 0

    def test_all_cells_empty(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {(0, 0): "", (0, 1): None, (1, 0): ""}}]}
        assert gnumeric_empty_cell_count(model, 0) == 3

    def test_mixed_empty_and_values(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {(0, 0): "hello", (0, 1): "", (1, 0): None, (1, 1): "42"}}]}
        assert gnumeric_empty_cell_count(model, 0) == 2

    def test_empty_grid(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {}}]}
        assert gnumeric_empty_cell_count(model, 0) == 0

    def test_invalid_sheet_index(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {}}]}
        assert gnumeric_empty_cell_count(model, 5) == 0

    def test_negative_sheet_index(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {}}]}
        assert gnumeric_empty_cell_count(model, -1) == 0

    def test_no_sheets(self):
        model = {"sheets": []}
        assert gnumeric_empty_cell_count(model, 0) == 0

    def test_complements_nonempty_count(self):
        model = {"sheets": [{"name": "S1", "cell_grid": {
            (0, 0): "a", (0, 1): "", (1, 0): "b", (1, 1): None
        }}]}
        empty = gnumeric_empty_cell_count(model, 0)
        nonempty = count_nonempty_cells(model, 0)
        total = len(model["sheets"][0]["cell_grid"])
        assert empty + nonempty == total

    def test_importable_from_init(self):
        from src.python.gnumeric import gnumeric_empty_cell_count as fn
        assert callable(fn)

    def test_in_all_list(self):
        from src.python.gnumeric import __all__
        assert "gnumeric_empty_cell_count" in __all__

    def test_on_real_file(self):
        samples = _REPO / "samples" / "by-format" / "gnumeric"
        if not samples.exists():
            pytest.skip("No gnumeric samples")
        files = list(samples.glob("*.gnumeric"))
        if not files:
            pytest.skip("No .gnumeric files")
        model = load(files[0])
        result = gnumeric_empty_cell_count(model, 0)
        assert result >= 0
