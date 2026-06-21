"""Tests for FODS Sprint 59 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_CELL_TY-001   (Fods Cell Type Variety)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_cell_type_variety

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsCellTypeVariety:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_cell_type_variety(wb), int)

    def test_exact_1_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_type_variety(wb) == 1

    def test_exact_1_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_type_variety(wb) == 1

    def test_exact_1_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_cell_type_variety(wb) == 1

    def test_exact_3_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_cell_type_variety(wb) == 3

    def test_positive(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_type_variety(wb) > 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_type_variety(wb) == fods_cell_type_variety(wb)
