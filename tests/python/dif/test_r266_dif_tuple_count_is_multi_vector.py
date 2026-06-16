"""Tests for dif_tuple_count and dif_is_multi_vector (Sprint 56)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from dif.dif_parser import dif_tuple_count, dif_is_multi_vector

DIF = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "dif" / "valid"


class TestDifTupleCount:
    def test_minimal_2x2(self):
        assert dif_tuple_count(DIF / "minimal-2x2.dif") == 2

    def test_numeric_row(self):
        assert dif_tuple_count(DIF / "numeric-row.dif") == 1

    def test_single_cell(self):
        assert dif_tuple_count(DIF / "single-cell.dif") == 1

    def test_returns_int(self):
        result = dif_tuple_count(DIF / "minimal-2x2.dif")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-2x2.dif", "numeric-row.dif", "single-cell.dif"]:
            assert dif_tuple_count(DIF / f) >= 0


class TestDifIsMultiVector:
    def test_minimal_2x2_is_multi(self):
        assert dif_is_multi_vector(DIF / "minimal-2x2.dif") is True

    def test_numeric_row_is_multi(self):
        assert dif_is_multi_vector(DIF / "numeric-row.dif") is True

    def test_single_cell_not_multi(self):
        assert dif_is_multi_vector(DIF / "single-cell.dif") is False

    def test_returns_bool(self):
        result = dif_is_multi_vector(DIF / "minimal-2x2.dif")
        assert isinstance(result, bool)

    def test_false_for_one_vector(self):
        assert dif_is_multi_vector(DIF / "single-cell.dif") is False
