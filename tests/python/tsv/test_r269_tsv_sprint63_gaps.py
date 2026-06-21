"""Tests for TSV Sprint 63 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_EMPTY_RO-001   (Tsv Empty Row Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_empty_row_ratio

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvEmptyRowRatio:
    def test_return_type(self):
        assert isinstance(tsv_empty_row_ratio(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert tsv_empty_row_ratio(_MINIMAL) == 0.0

    def test_zero_for_multi_column(self):
        assert tsv_empty_row_ratio(_MULTI) == 0.0

    def test_zero_for_single_cell(self):
        assert tsv_empty_row_ratio(_SINGLE) == 0.0

    def test_between_0_and_1(self):
        assert 0.0 <= tsv_empty_row_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert tsv_empty_row_ratio(_MINIMAL) == tsv_empty_row_ratio(_MINIMAL)
