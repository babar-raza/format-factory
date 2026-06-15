"""Tests for ods_row_count().

Sprint: product-deepening-rnext84
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_row_count

ODS_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsRowCount:
    def test_import(self):
        assert callable(ods_row_count)

    def test_minimal_spreadsheet_has_two_rows(self):
        assert ods_row_count(ODS_SAMPLES / "minimal-spreadsheet.ods") == 2

    def test_single_cell_has_one_row(self):
        assert ods_row_count(ODS_SAMPLES / "single-cell.ods") == 1

    def test_numeric_row_has_one_row(self):
        assert ods_row_count(ODS_SAMPLES / "numeric-row.ods") == 1

    def test_returns_int(self):
        result = ods_row_count(ODS_SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in ODS_SAMPLES.iterdir():
            if sample.suffix == ".ods":
                assert ods_row_count(sample) >= 0
