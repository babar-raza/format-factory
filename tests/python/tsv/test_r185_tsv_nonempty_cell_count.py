"""
tests/python/tsv/test_r185_tsv_nonempty_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT53-001
Tests for tsv_nonempty_cell_count() — count non-empty cells across all rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_nonempty_cell_count

SAMPLES = _REPO / "samples" / "by-format" / "tsv"


class TestTsvNonemptyCellCount:
    def test_single_cell_is_one(self):
        result = tsv_nonempty_cell_count(SAMPLES / "single-cell.tsv")
        assert result == 1

    def test_minimal_2x2_is_four(self):
        result = tsv_nonempty_cell_count(SAMPLES / "minimal-2x2.tsv")
        assert result == 4

    def test_multi_column_positive(self):
        result = tsv_nonempty_cell_count(SAMPLES / "multi-column.tsv")
        assert result > 1

    def test_returns_int(self):
        result = tsv_nonempty_cell_count(SAMPLES / "single-cell.tsv")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_nonempty_cell_count(SAMPLES / "minimal-2x2.tsv")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.tsv import tsv_nonempty_cell_count as fn
        result = fn(SAMPLES / "single-cell.tsv")
        assert result == 1
