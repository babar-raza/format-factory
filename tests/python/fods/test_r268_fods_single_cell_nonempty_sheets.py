"""Tests for fods_is_single_cell and fods_nonempty_sheet_count (Sprint 58)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fods.parser import parse_fods_strict
from fods.neutral_model import fods_is_single_cell, fods_nonempty_sheet_count

FODS = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fods"


class TestFodsIsSingleCell:
    def test_minimal_is_single_cell(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert fods_is_single_cell(wb) is True

    def test_multi_sheet_not_single_cell(self):
        wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
        assert fods_is_single_cell(wb) is False

    def test_formula_not_single_cell(self):
        wb = parse_fods_strict(FODS / "formula-basic.fods")
        assert fods_is_single_cell(wb) is False

    def test_returns_bool(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_is_single_cell(wb), bool)

    def test_false_when_multiple_cells(self):
        wb = parse_fods_strict(FODS / "formula-basic.fods")
        assert fods_is_single_cell(wb) is False


class TestFodsNonemptySheetCount:
    def test_minimal_one_nonempty(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert fods_nonempty_sheet_count(wb) == 1

    def test_multi_sheet_two_nonempty(self):
        wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
        assert fods_nonempty_sheet_count(wb) == 2

    def test_formula_one_nonempty(self):
        wb = parse_fods_strict(FODS / "formula-basic.fods")
        assert fods_nonempty_sheet_count(wb) == 1

    def test_returns_int(self):
        wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_nonempty_sheet_count(wb), int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods", "formula-basic.fods"]:
            wb = parse_fods_strict(FODS / f)
            assert fods_nonempty_sheet_count(wb) >= 0
