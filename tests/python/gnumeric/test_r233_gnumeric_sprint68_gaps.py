"""Tests for Gnumeric Sprint 68 gap closure.

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_MUL-001   (Gnumeric Multi Sheet Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_multi_sheet_ratio

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")
_EMPTY = str(_DIR / "empty-sheet.gnumeric")


class TestGnumericMultiSheetRatio:
    def test_return_type(self):
        assert isinstance(gnumeric_multi_sheet_ratio(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert gnumeric_multi_sheet_ratio(_MINIMAL) == 0.0

    def test_exact_1_0_for_multi(self):
        assert gnumeric_multi_sheet_ratio(_MULTI) == 1.0

    def test_zero_for_empty(self):
        assert gnumeric_multi_sheet_ratio(_EMPTY) == 0.0

    def test_between_0_and_1(self):
        assert 0.0 <= gnumeric_multi_sheet_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert gnumeric_multi_sheet_ratio(_MINIMAL) == gnumeric_multi_sheet_ratio(_MINIMAL)
