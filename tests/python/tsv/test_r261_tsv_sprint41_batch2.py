"""Tests for TSV Sprint 41 batch 2 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_HEADER_L-001  (Tsv Header Length Avg)
  GAP-TSV-FOSS-TSV_DATA_COM-001  (Tsv Data Completeness)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_data_completeness, tsv_header_length_avg

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvHeaderLengthAvg:
    def test_return_type(self):
        assert isinstance(tsv_header_length_avg(_MINIMAL_2X2), float)

    def test_exact_3_5_for_minimal_2x2(self):
        assert tsv_header_length_avg(_MINIMAL_2X2) == 3.5

    def test_exact_3_75_for_multi_column(self):
        assert tsv_header_length_avg(_MULTI_COLUMN) == 3.75

    def test_exact_5_0_for_single_cell(self):
        assert tsv_header_length_avg(_SINGLE_CELL) == 5.0

    def test_positive(self):
        assert tsv_header_length_avg(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_header_length_avg(_MINIMAL_2X2) == tsv_header_length_avg(_MINIMAL_2X2)


class TestTsvDataCompleteness:
    def test_return_type(self):
        assert isinstance(tsv_data_completeness(_MINIMAL_2X2), float)

    def test_exact_1_0_for_minimal_2x2(self):
        assert tsv_data_completeness(_MINIMAL_2X2) == 1.0

    def test_exact_1_0_for_multi_column(self):
        assert tsv_data_completeness(_MULTI_COLUMN) == 1.0

    def test_exact_1_0_for_single_cell(self):
        assert tsv_data_completeness(_SINGLE_CELL) == 1.0

    def test_nonnegative(self):
        assert tsv_data_completeness(_MINIMAL_2X2) >= 0.0

    def test_consistent_across_calls(self):
        assert tsv_data_completeness(_MINIMAL_2X2) == tsv_data_completeness(_MINIMAL_2X2)
