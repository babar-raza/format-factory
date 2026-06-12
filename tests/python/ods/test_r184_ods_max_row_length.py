"""
tests/python/ods/test_r184_ods_max_row_length.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT52-001
Tests for ods_max_row_length() — max number of cells in any single row.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_max_row_length

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsMaxRowLength:
    def test_single_cell_is_one(self):
        result = ods_max_row_length(SAMPLES / "single-cell.ods")
        assert result == 1

    def test_numeric_row_is_three(self):
        result = ods_max_row_length(SAMPLES / "numeric-row.ods")
        assert result == 3

    def test_minimal_spreadsheet_is_two(self):
        result = ods_max_row_length(SAMPLES / "minimal-spreadsheet.ods")
        assert result == 2

    def test_returns_int(self):
        result = ods_max_row_length(SAMPLES / "single-cell.ods")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ods_max_row_length(SAMPLES / "minimal-spreadsheet.ods")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.ods import ods_max_row_length as fn
        result = fn(SAMPLES / "single-cell.ods")
        assert result == 1
