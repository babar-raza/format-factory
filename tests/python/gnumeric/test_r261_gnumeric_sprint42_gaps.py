"""Tests for Gnumeric Sprint 42 gap closure.

Closes:
  GAP-Gnumeric-FOSS-GNUMERIC_DIS-001  (Gnumeric Distinct String Count)
  GAP-Gnumeric-FOSS-GNUMERIC_FIL-001  (Gnumeric File Size Bytes)
  GAP-Gnumeric-FOSS-GNUMERIC_UNI-001  (Gnumeric Unique Value Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_distinct_string_count,
    gnumeric_file_size_bytes,
    gnumeric_unique_value_count,
)

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")


class TestGnumericDistinctStringCount:
    def test_return_type(self):
        assert isinstance(gnumeric_distinct_string_count(_EMPTY), int)

    def test_zero_for_empty(self):
        assert gnumeric_distinct_string_count(_EMPTY) == 0

    def test_exact_4_for_multi(self):
        assert gnumeric_distinct_string_count(_MULTI) == 4

    def test_exact_1_for_minimal(self):
        assert gnumeric_distinct_string_count(_MINIMAL) == 1

    def test_nonnegative(self):
        assert gnumeric_distinct_string_count(_EMPTY) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_distinct_string_count(_MULTI) == gnumeric_distinct_string_count(_MULTI)


class TestGnumericFileSizeBytes:
    def test_return_type(self):
        assert isinstance(gnumeric_file_size_bytes(_EMPTY), int)

    def test_exact_264_for_empty(self):
        assert gnumeric_file_size_bytes(_EMPTY) == 264

    def test_exact_337_for_multi(self):
        assert gnumeric_file_size_bytes(_MULTI) == 337

    def test_positive(self):
        assert gnumeric_file_size_bytes(_EMPTY) > 0

    def test_consistent_across_calls(self):
        assert gnumeric_file_size_bytes(_EMPTY) == gnumeric_file_size_bytes(_EMPTY)


class TestGnumericUniqueValueCount:
    def test_return_type(self):
        assert isinstance(gnumeric_unique_value_count(_EMPTY), int)

    def test_zero_for_empty(self):
        assert gnumeric_unique_value_count(_EMPTY) == 0

    def test_exact_4_for_multi(self):
        assert gnumeric_unique_value_count(_MULTI) == 4

    def test_exact_1_for_minimal(self):
        assert gnumeric_unique_value_count(_MINIMAL) == 1

    def test_nonnegative(self):
        assert gnumeric_unique_value_count(_EMPTY) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_unique_value_count(_MULTI) == gnumeric_unique_value_count(_MULTI)
