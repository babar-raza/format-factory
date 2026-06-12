"""
tests/python/tsv/test_r197_tsv_analytics.py

Sprint: FORMAT-FACTORY-TSV-SYLK-DEEPENING-001
Tests for tsv_nonempty_cell_count(), tsv_numeric_cell_count(), tsv_empty_row_count().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import tsv_nonempty_cell_count, tsv_numeric_cell_count, tsv_empty_row_count

_SAMPLES = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.tsv")
_MULTI = str(_SAMPLES / "multi-column.tsv")


class TestTsvNonemptyCellCount:
    def test_returns_int(self):
        result = tsv_nonempty_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_real_file(self):
        result = tsv_nonempty_cell_count(_MINIMAL)
        assert result > 0

    def test_minimal_file_has_4_cells(self):
        result = tsv_nonempty_cell_count(_MINIMAL)
        assert result == 4

    def test_non_negative(self):
        result = tsv_nonempty_cell_count(_MINIMAL)
        assert result >= 0


class TestTsvNumericCellCount:
    def test_returns_int(self):
        result = tsv_numeric_cell_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = tsv_numeric_cell_count(_MINIMAL)
        assert result >= 0

    def test_count_le_total_cells(self):
        nonempty = tsv_nonempty_cell_count(_MINIMAL)
        numeric = tsv_numeric_cell_count(_MINIMAL)
        assert numeric <= nonempty


class TestTsvEmptyRowCount:
    def test_returns_int(self):
        result = tsv_empty_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_minimal_has_no_empty_rows(self):
        result = tsv_empty_row_count(_MINIMAL)
        assert result == 0

    def test_non_negative(self):
        result = tsv_empty_row_count(_MINIMAL)
        assert result >= 0
