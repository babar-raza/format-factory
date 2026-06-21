"""Tests for CSV Sprint 41 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_WIDEST_F-001  (Csv Widest Field Length)
  GAP-CSV-FOSS-CSV_NARROW_C-001  (Csv Narrow Column Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_narrow_column_count, csv_widest_field_length

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvWidestFieldLength:
    def test_return_type(self):
        assert isinstance(csv_widest_field_length(_MINIMAL_2X2), int)

    def test_exact_5_for_minimal_2x2(self):
        assert csv_widest_field_length(_MINIMAL_2X2) == 5

    def test_exact_22_for_quoted_fields(self):
        assert csv_widest_field_length(_QUOTED) == 22

    def test_positive(self):
        assert csv_widest_field_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_widest_field_length(_MINIMAL_2X2) == csv_widest_field_length(_MINIMAL_2X2)


class TestCsvNarrowColumnCount:
    def test_return_type(self):
        assert isinstance(csv_narrow_column_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert csv_narrow_column_count(_MINIMAL_2X2) == 2

    def test_exact_1_for_quoted_fields(self):
        assert csv_narrow_column_count(_QUOTED) == 1

    def test_nonnegative(self):
        assert csv_narrow_column_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_narrow_column_count(_MINIMAL_2X2) == csv_narrow_column_count(_MINIMAL_2X2)
