"""Tests for CSV gap closure batch 6 (Sprint 40).

Closes:
  GAP-CSV-FOSS-CSV_MAX_COLU-001   (Csv Max Column Name Length)
  GAP-CSV-FOSS-CSV_HAS_BLAN-001   (Csv Has Blank Headers)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_has_blank_headers, csv_max_column_name_length

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED_FIELDS = str(_DIR / "quoted-fields.csv")
_SINGLE_CELL = str(_DIR / "single-cell.csv")


class TestCsvMaxColumnNameLength:
    def test_return_type(self):
        assert isinstance(csv_max_column_name_length(_MINIMAL_2X2), int)

    def test_exact_4_for_minimal_2x2(self):
        assert csv_max_column_name_length(_MINIMAL_2X2) == 4

    def test_exact_11_for_quoted_fields(self):
        assert csv_max_column_name_length(_QUOTED_FIELDS) == 11

    def test_exact_5_for_single_cell(self):
        assert csv_max_column_name_length(_SINGLE_CELL) == 5

    def test_positive(self):
        assert csv_max_column_name_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_max_column_name_length(_MINIMAL_2X2) == csv_max_column_name_length(_MINIMAL_2X2)


class TestCsvHasBlankHeaders:
    def test_return_type(self):
        assert isinstance(csv_has_blank_headers(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        assert csv_has_blank_headers(_MINIMAL_2X2) is False

    def test_false_for_quoted_fields(self):
        assert csv_has_blank_headers(_QUOTED_FIELDS) is False

    def test_false_for_single_cell(self):
        assert csv_has_blank_headers(_SINGLE_CELL) is False

    def test_consistent_across_calls(self):
        assert csv_has_blank_headers(_MINIMAL_2X2) == csv_has_blank_headers(_MINIMAL_2X2)
