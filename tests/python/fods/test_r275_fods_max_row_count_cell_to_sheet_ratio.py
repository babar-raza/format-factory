"""Tests for fods_max_row_count and fods_cell_to_sheet_ratio (Sprint 65)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fods.parser import parse_fods_strict
from fods.neutral_model import fods_max_row_count, fods_cell_to_sheet_ratio

FODS = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fods"


class TestFodsMaxRowCount:
    def test_minimal(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert fods_max_row_count(wb) == 1

    def test_multi_sheet(self):
        wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
        assert fods_max_row_count(wb) == 2

    def test_formula(self):
        wb = parse_fods_strict(FODS / "formula-basic.fods")
        assert fods_max_row_count(wb) == 4

    def test_returns_int(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_max_row_count(wb), int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods", "formula-basic.fods"]:
            wb = parse_fods_strict(FODS / f)
            assert fods_max_row_count(wb) >= 0


class TestFodsCellToSheetRatio:
    def test_minimal(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert abs(fods_cell_to_sheet_ratio(wb) - 1.0) < 0.01

    def test_multi_sheet(self):
        wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
        assert abs(fods_cell_to_sheet_ratio(wb) - 2.5) < 0.01

    def test_formula(self):
        wb = parse_fods_strict(FODS / "formula-basic.fods")
        assert abs(fods_cell_to_sheet_ratio(wb) - 4.0) < 0.01

    def test_returns_float(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_cell_to_sheet_ratio(wb), float)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods", "formula-basic.fods"]:
            wb = parse_fods_strict(FODS / f)
            assert fods_cell_to_sheet_ratio(wb) >= 0.0
