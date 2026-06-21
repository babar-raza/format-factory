"""Tests for TSV Sprint 41 batch 3 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_FILE_SIZ-001  (Tsv File Size Bytes)
  GAP-TSV-FOSS-TSV_MIN_ROW_-001  (Tsv Min Row Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_file_size_bytes, tsv_min_row_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvFileSizeBytes:
    def test_return_type(self):
        assert isinstance(tsv_file_size_bytes(_MINIMAL_2X2), int)

    def test_exact_28_for_minimal_2x2(self):
        assert tsv_file_size_bytes(_MINIMAL_2X2) == 28

    def test_exact_57_for_multi_column(self):
        assert tsv_file_size_bytes(_MULTI_COLUMN) == 57

    def test_positive(self):
        assert tsv_file_size_bytes(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_file_size_bytes(_MINIMAL_2X2) == tsv_file_size_bytes(_MINIMAL_2X2)


class TestTsvMinRowLength:
    def test_return_type(self):
        assert isinstance(tsv_min_row_length(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_min_row_length(_MINIMAL_2X2) == 2

    def test_exact_4_for_multi_column(self):
        assert tsv_min_row_length(_MULTI_COLUMN) == 4

    def test_exact_1_for_single_cell(self):
        assert tsv_min_row_length(_SINGLE_CELL) == 1

    def test_positive(self):
        assert tsv_min_row_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_min_row_length(_MINIMAL_2X2) == tsv_min_row_length(_MINIMAL_2X2)
