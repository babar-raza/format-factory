"""Tests for TSV Sprint 41 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_SHORTEST-001  (Tsv Shortest Row Length)
  GAP-TSV-FOSS-TSV_HAS_ONLY-001  (Tsv Has Only Numeric)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_has_only_numeric, tsv_shortest_row_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvShortestRowLength:
    def test_return_type(self):
        assert isinstance(tsv_shortest_row_length(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_shortest_row_length(_MINIMAL_2X2) == 2

    def test_exact_4_for_multi_column(self):
        assert tsv_shortest_row_length(_MULTI_COLUMN) == 4

    def test_exact_1_for_single_cell(self):
        assert tsv_shortest_row_length(_SINGLE_CELL) == 1

    def test_positive(self):
        assert tsv_shortest_row_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_shortest_row_length(_MINIMAL_2X2) == tsv_shortest_row_length(_MINIMAL_2X2)


class TestTsvHasOnlyNumeric:
    def test_return_type(self):
        assert isinstance(tsv_has_only_numeric(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        assert tsv_has_only_numeric(_MINIMAL_2X2) is False

    def test_true_for_single_cell(self):
        assert tsv_has_only_numeric(_SINGLE_CELL) is True

    def test_consistent_across_calls(self):
        assert tsv_has_only_numeric(_MINIMAL_2X2) == tsv_has_only_numeric(_MINIMAL_2X2)
