"""Tests for Gnumeric Sprint 54 gap closure.

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_FOR-001  (Gnumeric Formula Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_formula_count

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")


class TestGnumericFormulaCount:
    def test_return_type(self):
        assert isinstance(gnumeric_formula_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert gnumeric_formula_count(_EMPTY) == 0

    def test_zero_for_minimal(self):
        assert gnumeric_formula_count(_MINIMAL) == 0

    def test_zero_for_multi_cell(self):
        assert gnumeric_formula_count(_MULTI) == 0

    def test_nonnegative(self):
        assert gnumeric_formula_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_formula_count(_MINIMAL) == gnumeric_formula_count(_MINIMAL)
