"""
tests/python/gnumeric/test_r181_gnumeric_sheet_summary.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT49-001
Tests for gnumeric_sheet_summary() — row/col/cell count summary.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import load, gnumeric_sheet_summary

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericSheetSummary:
    def test_multi_cell_summary(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_sheet_summary(model, 0)
        assert result["row_count"] == 2
        assert result["col_count"] == 2
        assert result["nonempty_cells"] == 4

    def test_empty_sheet_summary(self):
        model = load(SAMPLES / "empty-sheet.gnumeric")
        result = gnumeric_sheet_summary(model, 0)
        assert result["row_count"] == 0
        assert result["nonempty_cells"] == 0

    def test_returns_dict(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_sheet_summary(model, 0)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"row_count", "col_count", "nonempty_cells"}

    def test_all_values_are_int(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_sheet_summary(model, 0)
        for k, v in result.items():
            assert isinstance(v, int), f"{k} should be int"

    def test_nonempty_cells_non_negative(self):
        model = load(SAMPLES / "empty-sheet.gnumeric")
        result = gnumeric_sheet_summary(model, 0)
        assert result["nonempty_cells"] >= 0

    def test_exported_from_init(self):
        from src.python.gnumeric import gnumeric_sheet_summary as fn
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = fn(model, 0)
        assert "row_count" in result
