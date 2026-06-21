"""Tests for CSV Sprint 50 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_VALUE_SU-001  (Csv Value Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_value_sum

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")
_INVALID = str(_DIR / "invalid-unterminated-quote.csv")


class TestCsvValueSum:
    def test_return_type(self):
        assert isinstance(csv_value_sum(_MINIMAL), (int, float))

    def test_exact_55_for_minimal_2x2(self):
        assert csv_value_sum(_MINIMAL) == 55.0

    def test_exact_42_for_single_cell(self):
        assert csv_value_sum(_SINGLE) == 42.0

    def test_zero_for_invalid(self):
        assert csv_value_sum(_INVALID) == 0.0

    def test_nonnegative_for_minimal(self):
        assert csv_value_sum(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_value_sum(_MINIMAL) == csv_value_sum(_MINIMAL)
