"""Tests for TSV Sprint 45 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_STRING_F-001  (Tsv String Field Count)
  GAP-TSV-FOSS-TSV_TOTAL_FI-001  (Tsv Total Field Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_string_field_count, tsv_total_field_count

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvStringFieldCount:
    def test_return_type(self):
        assert isinstance(tsv_string_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_string_field_count(_MINIMAL) == 2

    def test_exact_4_for_multi_column(self):
        assert tsv_string_field_count(_MULTI) == 4

    def test_zero_for_single_cell(self):
        assert tsv_string_field_count(_SINGLE) == 0

    def test_nonnegative(self):
        assert tsv_string_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert tsv_string_field_count(_MINIMAL) == tsv_string_field_count(_MINIMAL)


class TestTsvTotalFieldCount:
    def test_return_type(self):
        assert isinstance(tsv_total_field_count(_MINIMAL), int)

    def test_exact_4_for_minimal_2x2(self):
        assert tsv_total_field_count(_MINIMAL) == 4

    def test_exact_8_for_multi_column(self):
        assert tsv_total_field_count(_MULTI) == 8

    def test_exact_1_for_single_cell(self):
        assert tsv_total_field_count(_SINGLE) == 1

    def test_positive(self):
        assert tsv_total_field_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_total_field_count(_MINIMAL) == tsv_total_field_count(_MINIMAL)
