"""Tests for dif_cells_per_tuple and dif_is_wider_than_tall (Sprint 71)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from dif.dif_parser import dif_cells_per_tuple, dif_is_wider_than_tall

DIF = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "dif" / "valid"


class TestDifCellsPerTuple:
    def test_minimal_2x2(self):
        assert abs(dif_cells_per_tuple(DIF / "minimal-2x2.dif") - 4.0) < 0.01

    def test_numeric_row(self):
        assert abs(dif_cells_per_tuple(DIF / "numeric-row.dif") - 3.0) < 0.01

    def test_single_cell(self):
        assert abs(dif_cells_per_tuple(DIF / "single-cell.dif") - 1.0) < 0.01

    def test_returns_float(self):
        assert isinstance(dif_cells_per_tuple(DIF / "minimal-2x2.dif"), float)

    def test_nonnegative(self):
        for f in ["minimal-2x2.dif", "numeric-row.dif", "single-cell.dif"]:
            assert dif_cells_per_tuple(DIF / f) >= 0.0


class TestDifIsWiderThanTall:
    def test_square_minimal(self):
        assert dif_is_wider_than_tall(DIF / "minimal-2x2.dif") is False

    def test_wider_numeric_row(self):
        assert dif_is_wider_than_tall(DIF / "numeric-row.dif") is True

    def test_square_single(self):
        assert dif_is_wider_than_tall(DIF / "single-cell.dif") is False

    def test_returns_bool(self):
        assert isinstance(dif_is_wider_than_tall(DIF / "minimal-2x2.dif"), bool)

    def test_all_files_return_bool(self):
        for f in ["minimal-2x2.dif", "numeric-row.dif", "single-cell.dif"]:
            assert isinstance(dif_is_wider_than_tall(DIF / f), bool)
