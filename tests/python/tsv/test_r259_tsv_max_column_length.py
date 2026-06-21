"""Tests for tsv_max_column_length (Sprint 40 batch 4).

Closes:
  GAP-TSV-FOSS-TSV_MAX_COLU-001  (Tsv Max Column Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_max_column_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvMaxColumnLength:
    def test_return_type(self):
        assert isinstance(tsv_max_column_length(_MINIMAL_2X2), int)

    def test_exact_8_for_minimal_2x2(self):
        assert tsv_max_column_length(_MINIMAL_2X2) == 8

    def test_exact_9_for_multi_column(self):
        assert tsv_max_column_length(_MULTI_COLUMN) == 9

    def test_exact_2_for_single_cell(self):
        assert tsv_max_column_length(_SINGLE_CELL) == 2

    def test_positive(self):
        assert tsv_max_column_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_max_column_length(_MINIMAL_2X2) == tsv_max_column_length(_MINIMAL_2X2)
