"""
test_r159_ods_all_values.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Added: 2026-06-10

Tests for ODS get_all_values function.
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import get_all_values

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestGetAllValues:
    def test_single_cell(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods", 0)
        assert "A1" in vals

    def test_numeric_row(self):
        vals = get_all_values(_SAMPLES / "numeric-row.ods", 0)
        assert 1.0 in vals
        assert 2.0 in vals
        assert 3.0 in vals

    def test_minimal_spreadsheet(self):
        vals = get_all_values(_SAMPLES / "minimal-spreadsheet.ods", 0)
        assert "Name" in vals

    def test_out_of_range_sheet(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods", 99)
        assert vals == []

    def test_returns_list(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods")
        assert isinstance(vals, list)

    def test_default_sheet_index(self):
        vals = get_all_values(_SAMPLES / "single-cell.ods")
        assert len(vals) >= 1
