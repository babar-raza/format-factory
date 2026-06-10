"""
test_r156_ods_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT15-001
Added: 2026-06-10

Tests for ODS get_cell_value, get_sheet_names, get_row_count functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import get_cell_value, get_sheet_names, get_row_count, OdsError

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestGetCellValue:
    def test_string_cell(self):
        val = get_cell_value(_SAMPLES / "minimal-spreadsheet.ods", 0, 0, 0)
        assert val == "Name"

    def test_float_cell(self):
        val = get_cell_value(_SAMPLES / "minimal-spreadsheet.ods", 0, 1, 1)
        assert val == 42.0

    def test_single_cell(self):
        val = get_cell_value(_SAMPLES / "single-cell.ods", 0, 0, 0)
        assert val == "A1"

    def test_numeric_row(self):
        val = get_cell_value(_SAMPLES / "numeric-row.ods", 0, 0, 0)
        assert val == 1.0

    def test_numeric_row_second_col(self):
        val = get_cell_value(_SAMPLES / "numeric-row.ods", 0, 0, 2)
        assert val == 3.0

    def test_out_of_range_sheet(self):
        val = get_cell_value(_SAMPLES / "single-cell.ods", 99, 0, 0)
        assert val is None

    def test_out_of_range_row(self):
        val = get_cell_value(_SAMPLES / "single-cell.ods", 0, 99, 0)
        assert val is None

    def test_out_of_range_col(self):
        val = get_cell_value(_SAMPLES / "single-cell.ods", 0, 0, 99)
        assert val is None

    def test_negative_index(self):
        val = get_cell_value(_SAMPLES / "single-cell.ods", 0, -1, 0)
        assert val is None


class TestGetSheetNames:
    def test_single_sheet(self):
        names = get_sheet_names(_SAMPLES / "minimal-spreadsheet.ods")
        assert names == ["Sheet1"]

    def test_single_cell_sheet(self):
        names = get_sheet_names(_SAMPLES / "single-cell.ods")
        assert len(names) >= 1
        assert "Sheet1" in names

    def test_returns_list(self):
        names = get_sheet_names(_SAMPLES / "numeric-row.ods")
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)


class TestGetRowCount:
    def test_minimal_spreadsheet(self):
        count = get_row_count(_SAMPLES / "minimal-spreadsheet.ods", 0)
        assert count == 2

    def test_single_cell(self):
        count = get_row_count(_SAMPLES / "single-cell.ods", 0)
        assert count == 1

    def test_numeric_row(self):
        count = get_row_count(_SAMPLES / "numeric-row.ods", 0)
        assert count == 1

    def test_out_of_range_sheet(self):
        count = get_row_count(_SAMPLES / "single-cell.ods", 99)
        assert count == 0

    def test_default_sheet_index(self):
        count = get_row_count(_SAMPLES / "single-cell.ods")
        assert count == 1
