"""Tests for ods_empty_row_count — counts rows where all cells are empty."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_empty_row_count, ods_row_count

ODS_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsEmptyRowCount:
    def test_import(self):
        assert callable(ods_empty_row_count)

    def test_returns_int(self):
        result = ods_empty_row_count(ODS_SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in ODS_SAMPLES.iterdir():
            if sample.suffix == ".ods":
                assert ods_empty_row_count(sample) >= 0

    def test_single_cell_has_zero_empty_rows(self):
        result = ods_empty_row_count(ODS_SAMPLES / "single-cell.ods")
        assert result == 0

    def test_numeric_row_has_zero_empty_rows(self):
        result = ods_empty_row_count(ODS_SAMPLES / "numeric-row.ods")
        assert result == 0

    def test_empty_row_count_leq_total_row_count(self):
        for sample in ODS_SAMPLES.iterdir():
            if sample.suffix == ".ods":
                empty = ods_empty_row_count(sample)
                total = ods_row_count(sample)
                assert empty <= total, f"{sample.name}: empty={empty} > total={total}"

    def test_invalid_sheet_index_returns_zero(self):
        result = ods_empty_row_count(ODS_SAMPLES / "single-cell.ods", sheet_index=99)
        assert result == 0

    def test_negative_sheet_index_returns_zero(self):
        result = ods_empty_row_count(ODS_SAMPLES / "single-cell.ods", sheet_index=-1)
        assert result == 0
