"""Tests for FODS Sprint 45 batch 2 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_MAX_CEL-001  (Fods Max Cell Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_max_cell_length, parse_fods_strict

_DIR = _REPO / "samples" / "by-format" / "fods"
_FORMULA = str(_DIR / "formula-basic.fods")
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsMaxCellLength:
    def test_return_type(self):
        doc = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_max_cell_length(doc), int)

    def test_exact_5_for_minimal(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_max_cell_length(doc) == 5

    def test_exact_11_for_typed_values(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_max_cell_length(doc) == 11

    def test_exact_4_for_formula_basic(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_max_cell_length(doc) == 4

    def test_nonnegative(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_max_cell_length(doc) >= 0

    def test_consistent_across_calls(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_max_cell_length(doc) == fods_max_cell_length(doc)
