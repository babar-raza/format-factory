"""Tests for FODS Sprint 70 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_CELL_VA-001   (Fods Cell Value Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_cell_value_variance, parse_fods_strict

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsCellValueVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_cell_value_variance(wb), (int, float))

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_value_variance(wb) == 0.0

    def test_exact_350_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_value_variance(wb) == 350.0

    def test_zero_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_cell_value_variance(wb) == 0.0

    def test_exact_430_5625_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_cell_value_variance(wb) == 430.5625

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_value_variance(wb) >= 0.0
