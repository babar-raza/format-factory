"""Tests for CSV Sprint 70 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_AVG_STRI-001   (Csv Avg String Field Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_avg_string_field_length

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvAvgStringFieldLength:
    def test_return_type(self):
        assert isinstance(csv_avg_string_field_length(_MINIMAL), (int, float))

    def test_exact_4_0_for_minimal(self):
        assert csv_avg_string_field_length(_MINIMAL) == 4.0

    def test_exact_13_0_for_quoted(self):
        assert csv_avg_string_field_length(_QUOTED) == 13.0

    def test_zero_for_single(self):
        assert csv_avg_string_field_length(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert csv_avg_string_field_length(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert csv_avg_string_field_length(_MINIMAL) == csv_avg_string_field_length(_MINIMAL)
