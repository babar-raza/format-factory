"""Tests for CSV Sprint 41 batch 4 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_FILE_SIZ-001  (Csv File Size Bytes)
  GAP-CSV-FOSS-CSV_TOTAL_FI-001  (Csv Total Field Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_file_size_bytes, csv_total_field_count

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvFileSizeBytes:
    def test_return_type(self):
        assert isinstance(csv_file_size_bytes(_MINIMAL_2X2), int)

    def test_exact_25_for_minimal_2x2(self):
        assert csv_file_size_bytes(_MINIMAL_2X2) == 25

    def test_exact_98_for_quoted_fields(self):
        assert csv_file_size_bytes(_QUOTED) == 98

    def test_positive(self):
        assert csv_file_size_bytes(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_file_size_bytes(_MINIMAL_2X2) == csv_file_size_bytes(_MINIMAL_2X2)


class TestCsvTotalFieldCount:
    def test_return_type(self):
        assert isinstance(csv_total_field_count(_MINIMAL_2X2), int)

    def test_exact_4_for_minimal_2x2(self):
        assert csv_total_field_count(_MINIMAL_2X2) == 4

    def test_exact_6_for_quoted_fields(self):
        assert csv_total_field_count(_QUOTED) == 6

    def test_exact_1_for_single_cell(self):
        assert csv_total_field_count(_SINGLE) == 1

    def test_positive(self):
        assert csv_total_field_count(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_total_field_count(_MINIMAL_2X2) == csv_total_field_count(_MINIMAL_2X2)
