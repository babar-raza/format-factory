"""Tests for gnumeric_column_count_file().

Sprint: product-deepening-rnext87
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import gnumeric_column_count_file

GNU_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericColumnCountFile:
    def test_import(self):
        assert callable(gnumeric_column_count_file)

    def test_empty_sheet_has_zero_columns(self):
        assert gnumeric_column_count_file(GNU_SAMPLES / "empty-sheet.gnumeric") == 0

    def test_minimal_spreadsheet_has_one_column(self):
        assert gnumeric_column_count_file(GNU_SAMPLES / "minimal-spreadsheet.gnumeric") == 1

    def test_multi_cell_basic_has_two_columns(self):
        assert gnumeric_column_count_file(GNU_SAMPLES / "multi-cell-basic.gnumeric") == 2

    def test_returns_int(self):
        result = gnumeric_column_count_file(GNU_SAMPLES / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in GNU_SAMPLES.iterdir():
            if sample.suffix == ".gnumeric":
                assert gnumeric_column_count_file(sample) >= 0
