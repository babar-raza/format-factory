"""Tests for Gnumeric Sprint 41 gap closure.

Closes:
  GAP-GNUMERIC-FOSS-GNUMERIC_ROW_-001  (Gnumeric Row Density)
  GAP-GNUMERIC-FOSS-GNUMERIC_STR-001  (Gnumeric String Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_row_density, gnumeric_string_density

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")


class TestGnumericRowDensity:
    def test_return_type(self):
        assert isinstance(gnumeric_row_density(_EMPTY), float)

    def test_exact_0_0_for_empty(self):
        assert gnumeric_row_density(_EMPTY) == 0.0

    def test_exact_1_0_for_multi(self):
        assert gnumeric_row_density(_MULTI) == 1.0

    def test_nonnegative(self):
        assert gnumeric_row_density(_EMPTY) >= 0.0

    def test_consistent_across_calls(self):
        assert gnumeric_row_density(_MULTI) == gnumeric_row_density(_MULTI)


class TestGnumericStringDensity:
    def test_return_type(self):
        assert isinstance(gnumeric_string_density(_EMPTY), float)

    def test_exact_0_0_for_empty(self):
        assert gnumeric_string_density(_EMPTY) == 0.0

    def test_exact_0_75_for_multi(self):
        assert gnumeric_string_density(_MULTI) == 0.75

    def test_exact_1_0_for_minimal(self):
        assert gnumeric_string_density(_MINIMAL) == 1.0

    def test_nonnegative(self):
        assert gnumeric_string_density(_EMPTY) >= 0.0

    def test_consistent_across_calls(self):
        assert gnumeric_string_density(_MULTI) == gnumeric_string_density(_MULTI)
