"""Tests for FODS Sprint 65 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_ROW_DEN-001   (Fods Row Density Avg)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_row_density_avg, parse_fods_strict

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsRowDensityAvg:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_row_density_avg(wb), (int, float))

    def test_exact_1_0_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_density_avg(wb) == 1.0

    def test_exact_1_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_row_density_avg(wb) == 1.0

    def test_exact_1_0_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_row_density_avg(wb) == 1.0

    def test_exact_1_0_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_row_density_avg(wb) == 1.0

    def test_between_0_and_1(self):
        wb = parse_fods_strict(_MINIMAL)
        assert 0.0 <= fods_row_density_avg(wb) <= 1.0
