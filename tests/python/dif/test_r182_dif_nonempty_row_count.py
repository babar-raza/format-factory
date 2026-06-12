"""
tests/python/dif/test_r182_dif_nonempty_row_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT50-001
Tests for dif_nonempty_row_count() — count rows with at least one non-empty cell.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_nonempty_row_count

SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifNonemptyRowCount:
    def test_minimal_2x2_has_nonempty_row(self):
        result = dif_nonempty_row_count(SAMPLES / "minimal-2x2.dif")
        assert result >= 1

    def test_numeric_row_has_nonempty_row(self):
        result = dif_nonempty_row_count(SAMPLES / "numeric-row.dif")
        assert result >= 1

    def test_single_cell_has_nonempty_row(self):
        result = dif_nonempty_row_count(SAMPLES / "single-cell.dif")
        assert result == 1

    def test_returns_int(self):
        result = dif_nonempty_row_count(SAMPLES / "single-cell.dif")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = dif_nonempty_row_count(SAMPLES / "minimal-2x2.dif")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.dif import dif_nonempty_row_count as fn
        result = fn(SAMPLES / "minimal-2x2.dif")
        assert result >= 1
