"""
Tests for additional DIF analytics gap closure (3 FOSS gaps).
Closes: DIF_COLUMN_D, DIF_VALUE_TY, DIF_TOTAL_CE
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_column_density,
    dif_value_type_variance,
    dif_total_cell_length,
)

_DIF_2x2 = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
_DIF_NUMERIC = _REPO / "samples/by-format/dif/valid/numeric-row.dif"
_DIF_SINGLE = _REPO / "samples/by-format/dif/valid/single-cell.dif"


class TestDifColumnDensity:
    def test_returns_float(self):
        assert isinstance(dif_column_density(_DIF_2x2), float)

    def test_2x2_full_density(self):
        # All cells filled → density = 1.0
        assert dif_column_density(_DIF_2x2) == pytest.approx(1.0)

    def test_numeric_full_density(self):
        assert dif_column_density(_DIF_NUMERIC) == pytest.approx(1.0)

    def test_bounded(self):
        assert 0.0 <= dif_column_density(_DIF_SINGLE) <= 1.0


class TestDifValueTypeVariance:
    def test_returns_float(self):
        assert isinstance(dif_value_type_variance(_DIF_2x2), float)

    def test_nonnegative(self):
        assert dif_value_type_variance(_DIF_2x2) >= 0.0

    def test_uniform_types_zero_variance(self):
        # numeric-row: all numeric → type variance = 0
        assert dif_value_type_variance(_DIF_NUMERIC) == pytest.approx(0.0)

    def test_2x2_zero_or_nonneg(self):
        assert dif_value_type_variance(_DIF_2x2) >= 0.0


class TestDifTotalCellLength:
    def test_returns_int(self):
        assert isinstance(dif_total_cell_length(_DIF_2x2), int)

    def test_nonnegative(self):
        assert dif_total_cell_length(_DIF_2x2) >= 0

    def test_2x2_exact(self):
        assert dif_total_cell_length(_DIF_2x2) == 36

    def test_numeric_less_than_2x2(self):
        # numeric-row has shorter string representations
        assert dif_total_cell_length(_DIF_NUMERIC) < dif_total_cell_length(_DIF_2x2)
