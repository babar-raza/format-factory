"""Tests for gnumeric_total_cell_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_total_cell_count, load, count_nonempty_cells

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericTotalCellCount:
    def test_minimal_spreadsheet(self):
        path = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
        count = gnumeric_total_cell_count(path)
        assert isinstance(count, int)
        assert count >= 1  # minimal has at least one cell

    def test_multi_cell_basic(self):
        path = str(_SAMPLES / "multi-cell-basic.gnumeric")
        count = gnumeric_total_cell_count(path)
        assert count >= 2  # multi-cell has multiple cells

    def test_empty_sheet(self):
        path = str(_SAMPLES / "empty-sheet.gnumeric")
        count = gnumeric_total_cell_count(path)
        assert count == 0  # empty sheet has no cells

    def test_matches_per_sheet_sum(self):
        """Total should equal sum of per-sheet counts."""
        path = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
        total = gnumeric_total_cell_count(path)
        model = load(path)
        sheets = model.get("sheets", [])
        manual_total = sum(count_nonempty_cells(model, i) for i in range(len(sheets)))
        assert total == manual_total

    def test_return_type(self):
        path = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_total_cell_count(path), int)

    def test_non_negative(self):
        path = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_cell_count(path) >= 0

    def test_importable_from_package(self):
        from gnumeric import gnumeric_total_cell_count as fn
        assert callable(fn)
