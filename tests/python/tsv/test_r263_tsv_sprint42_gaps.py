"""Tests for TSV Sprint 42 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_EMPTY_FI-001  (Tsv Empty Field Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_empty_field_count

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvEmptyFieldCount:
    def test_return_type(self):
        assert isinstance(tsv_empty_field_count(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert tsv_empty_field_count(_MINIMAL_2X2) == 0

    def test_zero_for_multi_column(self):
        assert tsv_empty_field_count(_MULTI_COLUMN) == 0

    def test_zero_for_single_cell(self):
        assert tsv_empty_field_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert tsv_empty_field_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_empty_field_count(_MINIMAL_2X2) == tsv_empty_field_count(_MINIMAL_2X2)
