"""Tests for gnumeric_distinct_value_count (Sprint 40 batch 2).

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_DIS-001  (Gnumeric Distinct Value Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_distinct_value_count

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")


class TestGnumericDistinctValueCount:
    def test_return_type(self):
        assert isinstance(gnumeric_distinct_value_count(_EMPTY), int)

    def test_zero_for_empty_sheet(self):
        assert gnumeric_distinct_value_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        assert gnumeric_distinct_value_count(_MINIMAL) == 1

    def test_exact_4_for_multi_cell(self):
        assert gnumeric_distinct_value_count(_MULTI) == 4

    def test_nonnegative(self):
        assert gnumeric_distinct_value_count(_EMPTY) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_distinct_value_count(_MINIMAL) == gnumeric_distinct_value_count(_MINIMAL)
