"""
tests/python/gnumeric/test_r185_gnumeric_numeric_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT53-001
Tests for gnumeric_numeric_cell_count() — count of numeric cells in a sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import load, gnumeric_numeric_cell_count

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericNumericCellCount:
    def test_multi_cell_basic_has_one_numeric(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_numeric_cell_count(model, 0)
        assert result >= 1

    def test_minimal_spreadsheet_no_numerics(self):
        model = load(SAMPLES / "minimal-spreadsheet.gnumeric")
        result = gnumeric_numeric_cell_count(model, 0)
        assert result == 0

    def test_returns_int(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_numeric_cell_count(model, 0)
        assert isinstance(result, int)

    def test_non_negative(self):
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = gnumeric_numeric_cell_count(model, 0)
        assert result >= 0

    def test_invalid_sheet_idx_returns_zero(self):
        model = load(SAMPLES / "minimal-spreadsheet.gnumeric")
        result = gnumeric_numeric_cell_count(model, 99)
        assert result == 0

    def test_exported_from_init(self):
        from src.python.gnumeric import gnumeric_numeric_cell_count as fn
        model = load(SAMPLES / "multi-cell-basic.gnumeric")
        result = fn(model, 0)
        assert isinstance(result, int)
