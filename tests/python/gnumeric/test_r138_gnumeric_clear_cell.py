"""Tests for clear_cell() — Gnumeric cell clearing.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-GNUMERIC-CLEAR-CELL
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import GnumericError, clear_cell, create_gnumeric, set_cell_value


class TestClearCell:
    def _model_with_cells(self):
        m = create_gnumeric([{"name": "Sheet1", "cells": []}])
        m = set_cell_value(m, 0, 0, 0, "A1")
        m = set_cell_value(m, 0, 0, 1, "B1")
        m = set_cell_value(m, 0, 1, 0, "A2")
        return m

    def test_clear_existing_cell(self):
        m = self._model_with_cells()
        assert m["sheets"][0]["cell_grid"].get((0, 0)) == "A1"
        result = clear_cell(m, 0, 0, 0)
        assert (0, 0) not in result["sheets"][0]["cell_grid"]

    def test_does_not_mutate_original(self):
        m = self._model_with_cells()
        clear_cell(m, 0, 0, 0)
        assert m["sheets"][0]["cell_grid"].get((0, 0)) == "A1"

    def test_clears_nonexistent_cell_no_error(self):
        m = self._model_with_cells()
        result = clear_cell(m, 0, 9, 9)
        assert (9, 9) not in result["sheets"][0]["cell_grid"]

    def test_cell_count_decreases(self):
        m = self._model_with_cells()
        before = m["sheets"][0]["cell_count"]
        result = clear_cell(m, 0, 0, 0)
        assert result["sheets"][0]["cell_count"] == before - 1

    def test_other_cells_preserved(self):
        m = self._model_with_cells()
        result = clear_cell(m, 0, 0, 0)
        assert result["sheets"][0]["cell_grid"].get((0, 1)) == "B1"
        assert result["sheets"][0]["cell_grid"].get((1, 0)) == "A2"

    def test_invalid_sheet_index_raises(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        with pytest.raises(GnumericError):
            clear_cell(m, 5, 0, 0)

    def test_negative_sheet_index_raises(self):
        m = create_gnumeric([{"name": "S1", "cells": []}])
        with pytest.raises(GnumericError):
            clear_cell(m, -1, 0, 0)

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            clear_cell("not a dict", 0, 0, 0)

    def test_returns_dict(self):
        m = self._model_with_cells()
        assert isinstance(clear_cell(m, 0, 0, 0), dict)

    def test_total_cell_count_updated(self):
        m = self._model_with_cells()
        result = clear_cell(m, 0, 0, 0)
        expected = sum(s["cell_count"] for s in result["sheets"])
        assert result["cell_count"] == expected
