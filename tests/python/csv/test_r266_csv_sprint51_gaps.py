"""Tests for CSV Sprint 51 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_BLANK_FI-001  (Csv Blank Field Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_blank_field_ratio

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_SINGLE = str(_DIR / "single-cell.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")


class TestCsvBlankFieldRatio:
    def test_return_type(self):
        assert isinstance(csv_blank_field_ratio(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert csv_blank_field_ratio(_MINIMAL) == 0.0

    def test_zero_for_single_cell(self):
        assert csv_blank_field_ratio(_SINGLE) == 0.0

    def test_zero_for_quoted(self):
        assert csv_blank_field_ratio(_QUOTED) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= csv_blank_field_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert csv_blank_field_ratio(_MINIMAL) == csv_blank_field_ratio(_MINIMAL)
