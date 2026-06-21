"""Tests for FODS Sprint 135 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_VALUE_V-001   (Fods Value Variance)
  GAP-FODS-FOSS-FODS_ROW_COL-001   (Fods Row Col Ratio)
  GAP-FODS-FOSS-FODS_ROW_FIL-001   (Fods Row Fill Rate)
  GAP-FODS-FOSS-FODS_CELL_EN-001   (Fods Cell Entropy)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods_strict, fods_value_variance, fods_row_col_ratio,
    fods_row_fill_rate, fods_cell_entropy,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")

_WB_MIN = None
_WB_FORM = None
_WB_TYPED = None


def _wb(path):
    return parse_fods_strict(path)


class TestFodsValueVariance:
    def test_return_type(self):
        assert isinstance(fods_value_variance(_wb(_MINIMAL)), (int, float))

    def test_exact_0_for_minimal(self):
        assert fods_value_variance(_wb(_MINIMAL)) == pytest.approx(0.0)

    def test_exact_350_for_formula(self):
        assert fods_value_variance(_wb(_FORMULA)) == pytest.approx(350.0)

    def test_exact_430_56_for_typed(self):
        assert fods_value_variance(_wb(_TYPED)) == pytest.approx(430.5625)

    def test_nonnegative(self):
        assert fods_value_variance(_wb(_MINIMAL)) >= 0.0

    def test_consistent(self):
        assert fods_value_variance(_wb(_MINIMAL)) == fods_value_variance(_wb(_MINIMAL))


class TestFodsRowColRatio:
    def test_return_type(self):
        assert isinstance(fods_row_col_ratio(_wb(_MINIMAL)), (int, float))

    def test_exact_1_for_minimal(self):
        assert fods_row_col_ratio(_wb(_MINIMAL)) == pytest.approx(1.0)

    def test_exact_4_for_formula(self):
        assert fods_row_col_ratio(_wb(_FORMULA)) == pytest.approx(4.0)

    def test_exact_2_for_typed(self):
        assert fods_row_col_ratio(_wb(_TYPED)) == pytest.approx(2.0)

    def test_nonnegative(self):
        assert fods_row_col_ratio(_wb(_MINIMAL)) >= 0.0

    def test_consistent(self):
        assert fods_row_col_ratio(_wb(_MINIMAL)) == fods_row_col_ratio(_wb(_MINIMAL))


class TestFodsRowFillRate:
    def test_return_type(self):
        assert isinstance(fods_row_fill_rate(_wb(_MINIMAL)), (int, float))

    def test_exact_1_for_minimal(self):
        assert fods_row_fill_rate(_wb(_MINIMAL)) == pytest.approx(1.0)

    def test_exact_1_for_formula(self):
        assert fods_row_fill_rate(_wb(_FORMULA)) == pytest.approx(1.0)

    def test_nonnegative(self):
        assert fods_row_fill_rate(_wb(_MINIMAL)) >= 0.0

    def test_at_most_1(self):
        assert fods_row_fill_rate(_wb(_MINIMAL)) <= 1.0

    def test_consistent(self):
        assert fods_row_fill_rate(_wb(_MINIMAL)) == fods_row_fill_rate(_wb(_MINIMAL))


class TestFodsCellEntropy:
    def test_return_type(self):
        assert isinstance(fods_cell_entropy(_wb(_MINIMAL)), (int, float))

    def test_approx_0_for_minimal(self):
        assert fods_cell_entropy(_wb(_MINIMAL)) == pytest.approx(0.0, abs=1e-9)

    def test_exact_2_for_formula(self):
        assert fods_cell_entropy(_wb(_FORMULA)) == pytest.approx(2.0)

    def test_exact_3_for_typed(self):
        assert fods_cell_entropy(_wb(_TYPED)) == pytest.approx(3.0)

    def test_nonnegative(self):
        assert fods_cell_entropy(_wb(_MINIMAL)) >= -1e-9

    def test_consistent(self):
        assert fods_cell_entropy(_wb(_MINIMAL)) == fods_cell_entropy(_wb(_MINIMAL))
