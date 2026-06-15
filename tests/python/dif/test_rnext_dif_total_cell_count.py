"""Tests for dif_total_cell_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_total_cell_count

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifTotalCellCount:
    def test_minimal(self):
        path = str(_SAMPLES / "single-cell.dif")
        count = dif_total_cell_count(path)
        assert isinstance(count, int)
        assert count >= 1

    def test_multi_row(self):
        path = str(_SAMPLES / "minimal-2x2.dif")
        count = dif_total_cell_count(path)
        assert count >= 2

    def test_numeric_only(self):
        path = str(_SAMPLES / "numeric-row.dif")
        count = dif_total_cell_count(path)
        assert count >= 1

    def test_return_type(self):
        path = str(_SAMPLES / "single-cell.dif")
        assert isinstance(dif_total_cell_count(path), int)

    def test_non_negative(self):
        path = str(_SAMPLES / "single-cell.dif")
        assert dif_total_cell_count(path) >= 0

    def test_at_least_as_many_as_numeric(self):
        from dif.dif_parser import dif_numeric_cell_count
        path = str(_SAMPLES / "minimal-2x2.dif")
        total = dif_total_cell_count(path)
        numeric = dif_numeric_cell_count(path)
        assert total >= numeric

    def test_importable_from_package(self):
        from dif import dif_total_cell_count as fn
        assert callable(fn)
