"""Tests for CSV Sprint 46 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_HEADER_U-001  (Csv Header Uniqueness Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_header_uniqueness_ratio

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_INVALID = str(_DIR / "invalid-unterminated-quote.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvHeaderUniquenessRatio:
    def test_return_type(self):
        assert isinstance(csv_header_uniqueness_ratio(_MINIMAL), (int, float))

    def test_exact_1_for_minimal_2x2(self):
        assert csv_header_uniqueness_ratio(_MINIMAL) == 1.0

    def test_exact_1_for_quoted_fields(self):
        assert csv_header_uniqueness_ratio(_QUOTED) == 1.0

    def test_exact_0_for_invalid(self):
        assert csv_header_uniqueness_ratio(_INVALID) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= csv_header_uniqueness_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert csv_header_uniqueness_ratio(_MINIMAL) == csv_header_uniqueness_ratio(_MINIMAL)
