"""
test_r161_ods_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Added: 2026-06-10

Tests for ODS get_cell_count function.
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import get_cell_count

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestGetCellCount:
    def test_single_cell(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods", 0)
        assert count >= 1

    def test_numeric_row(self):
        count = get_cell_count(_SAMPLES / "numeric-row.ods", 0)
        assert count >= 3

    def test_minimal_spreadsheet(self):
        count = get_cell_count(_SAMPLES / "minimal-spreadsheet.ods", 0)
        assert count >= 1

    def test_out_of_range_sheet(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods", 99)
        assert count == 0

    def test_default_sheet_index(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods")
        assert count >= 1

    def test_returns_int(self):
        count = get_cell_count(_SAMPLES / "single-cell.ods")
        assert isinstance(count, int)
