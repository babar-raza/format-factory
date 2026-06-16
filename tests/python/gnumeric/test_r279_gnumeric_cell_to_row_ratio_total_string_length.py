"""Tests for gnumeric_cell_to_row_ratio and gnumeric_total_string_length (Sprint 69)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_cell_to_row_ratio, gnumeric_total_string_length

GN = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "gnumeric"


class TestGnumericCellToRowRatio:
    def test_minimal(self):
        assert abs(gnumeric_cell_to_row_ratio(GN / "minimal-spreadsheet.gnumeric") - 1.0) < 0.01

    def test_multi_cell(self):
        assert abs(gnumeric_cell_to_row_ratio(GN / "multi-cell-basic.gnumeric") - 2.0) < 0.01

    def test_empty(self):
        assert abs(gnumeric_cell_to_row_ratio(GN / "empty-sheet.gnumeric") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(gnumeric_cell_to_row_ratio(GN / "minimal-spreadsheet.gnumeric"), float)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric", "empty-sheet.gnumeric"]:
            assert gnumeric_cell_to_row_ratio(GN / f) >= 0.0


class TestGnumericTotalStringLength:
    def test_minimal(self):
        assert gnumeric_total_string_length(GN / "minimal-spreadsheet.gnumeric") == 5

    def test_multi_cell(self):
        assert gnumeric_total_string_length(GN / "multi-cell-basic.gnumeric") == 16

    def test_empty(self):
        assert gnumeric_total_string_length(GN / "empty-sheet.gnumeric") == 0

    def test_returns_int(self):
        assert isinstance(gnumeric_total_string_length(GN / "minimal-spreadsheet.gnumeric"), int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric", "empty-sheet.gnumeric"]:
            assert gnumeric_total_string_length(GN / f) >= 0
