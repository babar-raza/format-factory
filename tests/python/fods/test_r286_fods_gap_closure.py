"""
Tests for FODS gap closure (1 FOSS function).
Closes: GAP-FODS-FOSS-FODS_HAS_NUM-001

Known sample values (via parse_fods_strict + fods_has_numeric_cells):
  formula-basic.fods: True
  minimal-spreadsheet.fods: False
  multi-sheet-basic.fods: False
  typed-values-basic.fods: True
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods_strict
from fods.neutral_model import fods_has_numeric_cells

_FODS = _REPO / "samples" / "by-format" / "fods"
_FORMULA = _FODS / "formula-basic.fods"
_MINIMAL = _FODS / "minimal-spreadsheet.fods"
_MULTI = _FODS / "multi-sheet-basic.fods"
_TYPED = _FODS / "typed-values-basic.fods"


def _parse(path):
    return parse_fods_strict(path)


class TestFodsHasNumericCells:
    def test_returns_bool(self):
        assert isinstance(fods_has_numeric_cells(_parse(_FORMULA)), bool)

    def test_formula_has_numeric(self):
        assert fods_has_numeric_cells(_parse(_FORMULA)) is True

    def test_minimal_no_numeric(self):
        assert fods_has_numeric_cells(_parse(_MINIMAL)) is False

    def test_multi_no_numeric(self):
        assert fods_has_numeric_cells(_parse(_MULTI)) is False

    def test_typed_values_has_numeric(self):
        assert fods_has_numeric_cells(_parse(_TYPED)) is True

    def test_all_return_bool(self):
        for p in [_FORMULA, _MINIMAL, _MULTI, _TYPED]:
            result = fods_has_numeric_cells(_parse(p))
            assert result is True or result is False
