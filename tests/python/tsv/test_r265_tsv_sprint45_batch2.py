"""Tests for TSV Sprint 45 batch 2 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_COLUMN_C-001  (Tsv Column Count Avg)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_column_count_avg

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvColumnCountAvg:
    def test_return_type(self):
        assert isinstance(tsv_column_count_avg(_MINIMAL), (int, float))

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_column_count_avg(_MINIMAL) == 2.0

    def test_exact_4_for_multi_column(self):
        assert tsv_column_count_avg(_MULTI) == 4.0

    def test_exact_1_for_single_cell(self):
        assert tsv_column_count_avg(_SINGLE) == 1.0

    def test_positive(self):
        assert tsv_column_count_avg(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_column_count_avg(_MINIMAL) == tsv_column_count_avg(_MINIMAL)
