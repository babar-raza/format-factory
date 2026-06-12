"""
test_r157_ods_column_row.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT16-001
Added: 2026-06-10

Tests for ODS get_column_count and get_row_values functions.
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import get_column_count, get_row_values

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestGetColumnCount:
    def test_minimal_spreadsheet(self):
        count = get_column_count(_SAMPLES / "minimal-spreadsheet.ods", 0)
        assert count >= 2

    def test_single_cell(self):
        count = get_column_count(_SAMPLES / "single-cell.ods", 0)
        assert count >= 1

    def test_numeric_row(self):
        count = get_column_count(_SAMPLES / "numeric-row.ods", 0)
        assert count >= 3

    def test_out_of_range_sheet(self):
        count = get_column_count(_SAMPLES / "single-cell.ods", 99)
        assert count == 0

    def test_default_sheet_index(self):
        count = get_column_count(_SAMPLES / "single-cell.ods")
        assert count >= 1


class TestGetRowValues:
    def test_header_row(self):
        vals = get_row_values(_SAMPLES / "minimal-spreadsheet.ods", 0, 0)
        assert "Name" in vals

    def test_data_row(self):
        vals = get_row_values(_SAMPLES / "minimal-spreadsheet.ods", 0, 1)
        assert 42.0 in vals

    def test_single_cell_row(self):
        vals = get_row_values(_SAMPLES / "single-cell.ods", 0, 0)
        assert vals == ["A1"]

    def test_numeric_row(self):
        vals = get_row_values(_SAMPLES / "numeric-row.ods", 0, 0)
        assert 1.0 in vals
        assert 2.0 in vals
        assert 3.0 in vals

    def test_out_of_range_sheet(self):
        vals = get_row_values(_SAMPLES / "single-cell.ods", 99, 0)
        assert vals == []

    def test_out_of_range_row(self):
        vals = get_row_values(_SAMPLES / "single-cell.ods", 0, 99)
        assert vals == []

    def test_negative_row(self):
        vals = get_row_values(_SAMPLES / "single-cell.ods", 0, -1)
        assert vals == []

    def test_returns_list(self):
        vals = get_row_values(_SAMPLES / "minimal-spreadsheet.ods", 0, 0)
        assert isinstance(vals, list)
