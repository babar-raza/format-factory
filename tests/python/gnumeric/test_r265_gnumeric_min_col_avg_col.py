"""Tests for gnumeric_min_column_count and gnumeric_avg_column_count (Sprint 55)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_min_column_count, gnumeric_avg_column_count

GNUMERIC = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "gnumeric"


class TestGnumericMinColumnCount:
    def test_minimal_spreadsheet(self):
        assert gnumeric_min_column_count(GNUMERIC / "minimal-spreadsheet.gnumeric") == 1

    def test_multi_cell_basic(self):
        assert gnumeric_min_column_count(GNUMERIC / "multi-cell-basic.gnumeric") == 2

    def test_empty_sheet(self):
        assert gnumeric_min_column_count(GNUMERIC / "empty-sheet.gnumeric") == 0

    def test_returns_int(self):
        result = gnumeric_min_column_count(GNUMERIC / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric", "empty-sheet.gnumeric"]:
            assert gnumeric_min_column_count(GNUMERIC / f) >= 0


class TestGnumericAvgColumnCount:
    def test_minimal_spreadsheet(self):
        assert gnumeric_avg_column_count(GNUMERIC / "minimal-spreadsheet.gnumeric") == 1.0

    def test_multi_cell_basic(self):
        assert gnumeric_avg_column_count(GNUMERIC / "multi-cell-basic.gnumeric") == 2.0

    def test_empty_sheet(self):
        assert gnumeric_avg_column_count(GNUMERIC / "empty-sheet.gnumeric") == 0.0

    def test_returns_float(self):
        result = gnumeric_avg_column_count(GNUMERIC / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric", "empty-sheet.gnumeric"]:
            assert gnumeric_avg_column_count(GNUMERIC / f) >= 0.0
