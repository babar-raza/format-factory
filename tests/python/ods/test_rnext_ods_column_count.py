"""Tests for ods_column_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_column_count

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsColumnCount:
    def test_minimal_spreadsheet(self):
        path = str(_SAMPLES / "minimal-spreadsheet.ods")
        count = ods_column_count(path)
        assert isinstance(count, int)
        assert count >= 1

    def test_multi_cell(self):
        path = str(_SAMPLES / "numeric-row.ods")
        count = ods_column_count(path)
        assert count >= 2

    def test_empty_sheet(self):
        path = str(_SAMPLES / "single-cell.ods")
        count = ods_column_count(path)
        assert count >= 0

    def test_out_of_range_sheet(self):
        path = str(_SAMPLES / "minimal-spreadsheet.ods")
        assert ods_column_count(path, sheet_index=999) == 0

    def test_negative_sheet_index(self):
        path = str(_SAMPLES / "minimal-spreadsheet.ods")
        assert ods_column_count(path, sheet_index=-1) == 0

    def test_return_type(self):
        path = str(_SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(ods_column_count(path), int)

    def test_non_negative(self):
        path = str(_SAMPLES / "minimal-spreadsheet.ods")
        assert ods_column_count(path) >= 0

    def test_importable_from_package(self):
        from ods import ods_column_count as fn
        assert callable(fn)
