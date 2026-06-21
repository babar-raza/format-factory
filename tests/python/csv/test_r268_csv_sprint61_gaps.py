"""Tests for CSV Sprint 61 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_HEADER_T-001   (Csv Header Total Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_header_total_length

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvHeaderTotalLength:
    def test_return_type(self):
        assert isinstance(csv_header_total_length(_MINIMAL), int)

    def test_exact_7_for_minimal(self):
        assert csv_header_total_length(_MINIMAL) == 7

    def test_exact_20_for_quoted(self):
        assert csv_header_total_length(_QUOTED) == 20

    def test_exact_5_for_single(self):
        assert csv_header_total_length(_SINGLE) == 5

    def test_positive(self):
        assert csv_header_total_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert csv_header_total_length(_MINIMAL) == csv_header_total_length(_MINIMAL)
