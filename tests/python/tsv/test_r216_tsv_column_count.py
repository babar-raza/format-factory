"""Tests for tsv_column_count().

Sprint: product-deepening-rnext86
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_column_count

TSV_SAMPLES = _REPO / "samples" / "by-format" / "tsv"


class TestTsvColumnCount:
    def test_import(self):
        assert callable(tsv_column_count)

    def test_minimal_2x2_has_two_columns(self):
        assert tsv_column_count(TSV_SAMPLES / "minimal-2x2.tsv") == 2

    def test_single_cell_has_one_column(self):
        assert tsv_column_count(TSV_SAMPLES / "single-cell.tsv") == 1

    def test_multi_column_has_four_columns(self):
        assert tsv_column_count(TSV_SAMPLES / "multi-column.tsv") == 4

    def test_returns_int(self):
        result = tsv_column_count(TSV_SAMPLES / "minimal-2x2.tsv")
        assert isinstance(result, int)

    def test_positive(self):
        for sample in TSV_SAMPLES.iterdir():
            if sample.suffix == ".tsv" and "invalid" not in sample.name:
                assert tsv_column_count(sample) >= 1
