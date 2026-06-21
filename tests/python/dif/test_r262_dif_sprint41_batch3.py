"""Tests for DIF Sprint 41 batch 3 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_FILE_SIZ-001  (Dif File Size Bytes)
  GAP-DIF-FOSS-DIF_UNIQUE_S-001  (Dif Unique String Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_file_size_bytes, dif_unique_string_count

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")
_SINGLE_CELL = str(_DIR / "single-cell.dif")


class TestDifFileSizeBytes:
    def test_return_type(self):
        assert isinstance(dif_file_size_bytes(_MINIMAL_2X2), int)

    def test_exact_187_for_minimal_2x2(self):
        assert dif_file_size_bytes(_MINIMAL_2X2) == 187

    def test_exact_123_for_numeric_row(self):
        assert dif_file_size_bytes(_NUMERIC_ROW) == 123

    def test_positive(self):
        assert dif_file_size_bytes(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert dif_file_size_bytes(_MINIMAL_2X2) == dif_file_size_bytes(_MINIMAL_2X2)


class TestDifUniqueStringCount:
    def test_return_type(self):
        assert isinstance(dif_unique_string_count(_MINIMAL_2X2), int)

    def test_exact_1_for_minimal_2x2(self):
        assert dif_unique_string_count(_MINIMAL_2X2) == 1

    def test_zero_for_numeric_row(self):
        assert dif_unique_string_count(_NUMERIC_ROW) == 0

    def test_zero_for_single_cell(self):
        assert dif_unique_string_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert dif_unique_string_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_unique_string_count(_MINIMAL_2X2) == dif_unique_string_count(_MINIMAL_2X2)
