"""Tests for tsv_max_field_count and tsv_is_multi_row (Sprint 55)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from tsv.tsv_parser import tsv_max_field_count, tsv_is_multi_row

TSV = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "tsv"


class TestTsvMaxFieldCount:
    def test_minimal_2x2(self):
        assert tsv_max_field_count(TSV / "minimal-2x2.tsv") == 2

    def test_single_cell(self):
        assert tsv_max_field_count(TSV / "single-cell.tsv") == 1

    def test_multi_column(self):
        assert tsv_max_field_count(TSV / "multi-column.tsv") == 4

    def test_returns_int(self):
        result = tsv_max_field_count(TSV / "minimal-2x2.tsv")
        assert isinstance(result, int)

    def test_positive(self):
        for f in ["minimal-2x2.tsv", "single-cell.tsv", "multi-column.tsv"]:
            assert tsv_max_field_count(TSV / f) >= 1


class TestTsvIsMultiRow:
    def test_minimal_2x2_is_multi(self):
        assert tsv_is_multi_row(TSV / "minimal-2x2.tsv") is True

    def test_single_cell_not_multi(self):
        assert tsv_is_multi_row(TSV / "single-cell.tsv") is False

    def test_multi_column_is_multi(self):
        assert tsv_is_multi_row(TSV / "multi-column.tsv") is True

    def test_returns_bool(self):
        result = tsv_is_multi_row(TSV / "minimal-2x2.tsv")
        assert isinstance(result, bool)

    def test_false_for_single_row(self):
        assert tsv_is_multi_row(TSV / "single-cell.tsv") is False
