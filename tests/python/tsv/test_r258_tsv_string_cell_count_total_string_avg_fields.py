"""Tests for TSV gap closure batch 2 (Sprint 40).

Closes:
  GAP-TSV-FOSS-TSV_STRING_C-001   (Tsv String Cell Count)
  GAP-TSV-FOSS-TSV_TOTAL_ST-001   (Tsv Total String Length)
  GAP-TSV-FOSS-TSV_AVG_FIEL-001   (Tsv Avg Fields Per Row)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_avg_fields_per_row, tsv_string_cell_count, tsv_total_string_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvStringCellCount:
    def test_return_type(self):
        assert isinstance(tsv_string_cell_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_string_cell_count(_MINIMAL_2X2) == 2

    def test_exact_4_for_multi_column(self):
        assert tsv_string_cell_count(_MULTI_COLUMN) == 4

    def test_nonnegative(self):
        assert tsv_string_cell_count(_SINGLE_CELL) >= 0

    def test_consistent_across_calls(self):
        assert tsv_string_cell_count(_MINIMAL_2X2) == tsv_string_cell_count(_MINIMAL_2X2)


class TestTsvTotalStringLength:
    def test_return_type(self):
        assert isinstance(tsv_total_string_length(_MINIMAL_2X2), int)

    def test_exact_12_for_minimal_2x2(self):
        assert tsv_total_string_length(_MINIMAL_2X2) == 12

    def test_exact_27_for_multi_column(self):
        assert tsv_total_string_length(_MULTI_COLUMN) == 27

    def test_nonnegative(self):
        assert tsv_total_string_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_total_string_length(_MINIMAL_2X2) == tsv_total_string_length(_MINIMAL_2X2)


class TestTsvAvgFieldsPerRow:
    def test_return_type(self):
        assert isinstance(tsv_avg_fields_per_row(_MINIMAL_2X2), float)

    def test_exact_2_0_for_minimal_2x2(self):
        assert tsv_avg_fields_per_row(_MINIMAL_2X2) == 2.0

    def test_exact_4_0_for_multi_column(self):
        assert tsv_avg_fields_per_row(_MULTI_COLUMN) == 4.0

    def test_positive(self):
        assert tsv_avg_fields_per_row(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_avg_fields_per_row(_MINIMAL_2X2) == tsv_avg_fields_per_row(_MINIMAL_2X2)
