"""Tests for tsv_is_square and tsv_cell_to_row_ratio (Sprint 68)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from tsv.tsv_parser import tsv_is_square, tsv_cell_to_row_ratio

TSV = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "tsv"


class TestTsvIsSquare:
    def test_minimal_is_square(self):
        assert tsv_is_square(TSV / "minimal-2x2.tsv") is True

    def test_multi_column_not_square(self):
        assert tsv_is_square(TSV / "multi-column.tsv") is False

    def test_single_cell_is_square(self):
        assert tsv_is_square(TSV / "single-cell.tsv") is True

    def test_returns_bool(self):
        assert isinstance(tsv_is_square(TSV / "minimal-2x2.tsv"), bool)

    def test_all_files(self):
        results = [tsv_is_square(TSV / f) for f in ["minimal-2x2.tsv", "multi-column.tsv", "single-cell.tsv"]]
        assert any(r is True for r in results)
        assert any(r is False for r in results)


class TestTsvCellToRowRatio:
    def test_minimal(self):
        assert abs(tsv_cell_to_row_ratio(TSV / "minimal-2x2.tsv") - 2.0) < 0.01

    def test_multi_column(self):
        assert abs(tsv_cell_to_row_ratio(TSV / "multi-column.tsv") - 4.0) < 0.01

    def test_single_cell(self):
        assert abs(tsv_cell_to_row_ratio(TSV / "single-cell.tsv") - 1.0) < 0.01

    def test_returns_float(self):
        assert isinstance(tsv_cell_to_row_ratio(TSV / "minimal-2x2.tsv"), float)

    def test_nonnegative(self):
        for f in ["minimal-2x2.tsv", "multi-column.tsv", "single-cell.tsv"]:
            assert tsv_cell_to_row_ratio(TSV / f) >= 0.0
