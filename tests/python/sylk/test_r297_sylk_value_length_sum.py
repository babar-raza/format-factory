"""Tests for sylk_total_string_length as value length sum (Sprint 40 batch 2).

Closes:
  GAP-SYLK-FOSS-SYLK_VALUE_L-001  (Sylk Value Length Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_total_string_length

_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.slk")
_NUMERIC_ROW = str(_DIR / "numeric-row.slk")
_SINGLE_CELL = str(_DIR / "single-cell.slk")


class TestSylkValueLengthSum:
    def test_return_type(self):
        assert isinstance(sylk_total_string_length(_MINIMAL_2X2), int)

    def test_exact_16_for_minimal_2x2(self):
        assert sylk_total_string_length(_MINIMAL_2X2) == 16

    def test_exact_3_for_numeric_row(self):
        assert sylk_total_string_length(_NUMERIC_ROW) == 3

    def test_exact_2_for_single_cell(self):
        assert sylk_total_string_length(_SINGLE_CELL) == 2

    def test_nonnegative(self):
        assert sylk_total_string_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert sylk_total_string_length(_MINIMAL_2X2) == sylk_total_string_length(_MINIMAL_2X2)
