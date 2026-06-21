"""Tests for DIF Sprint 45 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_STRING_F-001  (Dif String Field Count)
  GAP-DIF-FOSS-DIF_TOTAL_CH-001  (Dif Total Char Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_string_field_count, dif_total_char_count

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifStringFieldCount:
    def test_return_type(self):
        assert isinstance(dif_string_field_count(_MINIMAL), int)

    def test_exact_6_for_minimal_2x2(self):
        assert dif_string_field_count(_MINIMAL) == 6

    def test_zero_for_numeric_row(self):
        assert dif_string_field_count(_NUMERIC) == 0

    def test_zero_for_single_cell(self):
        assert dif_string_field_count(_SINGLE) == 0

    def test_nonnegative(self):
        assert dif_string_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_string_field_count(_MINIMAL) == dif_string_field_count(_MINIMAL)


class TestDifTotalCharCount:
    def test_return_type(self):
        assert isinstance(dif_total_char_count(_MINIMAL), int)

    def test_exact_28_for_minimal_2x2(self):
        assert dif_total_char_count(_MINIMAL) == 28

    def test_zero_for_numeric_row(self):
        assert dif_total_char_count(_NUMERIC) == 0

    def test_nonnegative(self):
        assert dif_total_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_total_char_count(_MINIMAL) == dif_total_char_count(_MINIMAL)
