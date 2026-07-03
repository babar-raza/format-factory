"""Tests for ods_is_single_cell and ods_min_row_length (Sprint 59)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from ods.ods_analytics import ods_is_single_cell, ods_min_row_length

ODS = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods" / "valid"


class TestOdsIsSingleCell:
    def test_minimal_not_single(self):
        assert ods_is_single_cell(ODS / "minimal-spreadsheet.ods") is False

    def test_numeric_row_not_single(self):
        assert ods_is_single_cell(ODS / "numeric-row.ods") is False

    def test_single_cell_is_single(self):
        assert ods_is_single_cell(ODS / "single-cell.ods") is True

    def test_returns_bool(self):
        result = ods_is_single_cell(ODS / "single-cell.ods")
        assert isinstance(result, bool)

    def test_false_for_multiple_cells(self):
        assert ods_is_single_cell(ODS / "minimal-spreadsheet.ods") is False


class TestOdsMinRowLength:
    def test_minimal_min_two(self):
        assert ods_min_row_length(ODS / "minimal-spreadsheet.ods") == 2

    def test_numeric_row_min_three(self):
        assert ods_min_row_length(ODS / "numeric-row.ods") == 3

    def test_single_cell_min_one(self):
        assert ods_min_row_length(ODS / "single-cell.ods") == 1

    def test_returns_int(self):
        result = ods_min_row_length(ODS / "minimal-spreadsheet.ods")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]:
            assert ods_min_row_length(ODS / f) >= 0
