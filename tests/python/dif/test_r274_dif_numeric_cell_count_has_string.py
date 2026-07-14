"""Tests for dif_numeric_cell_count and dif_has_string_cells (Sprint 64)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from dif import dif_numeric_cell_count, dif_has_string_cells

DIF = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "dif" / "valid"


class TestDifNumericCellCount:
    def test_minimal_2x2(self):
        assert dif_numeric_cell_count(DIF / "minimal-2x2.dif") == 2

    def test_numeric_row(self):
        assert dif_numeric_cell_count(DIF / "numeric-row.dif") == 3

    def test_single_cell(self):
        assert dif_numeric_cell_count(DIF / "single-cell.dif") == 1

    def test_returns_int(self):
        assert isinstance(dif_numeric_cell_count(DIF / "minimal-2x2.dif"), int)

    def test_positive(self):
        for f in ["minimal-2x2.dif", "numeric-row.dif", "single-cell.dif"]:
            assert dif_numeric_cell_count(DIF / f) > 0


class TestDifHasStringCells:
    def test_minimal_has_strings(self):
        assert dif_has_string_cells(DIF / "minimal-2x2.dif") is True

    def test_numeric_row_no_strings(self):
        assert dif_has_string_cells(DIF / "numeric-row.dif") is False

    def test_single_cell_no_strings(self):
        assert dif_has_string_cells(DIF / "single-cell.dif") is False

    def test_returns_bool(self):
        assert isinstance(dif_has_string_cells(DIF / "minimal-2x2.dif"), bool)

    def test_false_for_all_numeric(self):
        assert dif_has_string_cells(DIF / "numeric-row.dif") is False
