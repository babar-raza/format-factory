"""
tests/python/ods/test_r190_ods_numeric_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for ods_numeric_cell_count() — count of numeric cells in an ODS sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_numeric_cell_count

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsNumericCellCount:
    def test_numeric_row_returns_positive_count(self):
        """ODS file with numeric row returns count > 0."""
        result = ods_numeric_cell_count(SAMPLES / "numeric-row.ods")
        assert result > 0

    def test_result_is_int(self):
        """Result is always an integer."""
        result = ods_numeric_cell_count(SAMPLES / "numeric-row.ods")
        assert isinstance(result, int)

    def test_minimal_spreadsheet_returns_nonnegative(self):
        """Any ODS file returns result >= 0."""
        result = ods_numeric_cell_count(SAMPLES / "minimal-spreadsheet.ods")
        assert result >= 0

    def test_invalid_sheet_index_returns_zero(self):
        """Out-of-range sheet_index returns 0."""
        result = ods_numeric_cell_count(SAMPLES / "numeric-row.ods", sheet_index=999)
        assert result == 0

    def test_default_uses_sheet_zero(self):
        """Default sheet_index=0 same as explicit sheet_index=0."""
        r1 = ods_numeric_cell_count(SAMPLES / "numeric-row.ods")
        r2 = ods_numeric_cell_count(SAMPLES / "numeric-row.ods", sheet_index=0)
        assert r1 == r2

    def test_single_cell_returns_count(self):
        """single-cell.ods returns 0 or 1 depending on content."""
        result = ods_numeric_cell_count(SAMPLES / "single-cell.ods")
        assert isinstance(result, int) and result >= 0
