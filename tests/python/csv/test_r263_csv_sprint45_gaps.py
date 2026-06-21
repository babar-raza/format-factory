"""Tests for CSV Sprint 45 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_ROW_WIDT-001  (Csv Row Width Avg)
  GAP-CSV-FOSS-CSV_STRING_F-001  (Csv String Field Count)
  GAP-CSV-FOSS-CSV_MAX_STRI-001  (Csv Max String Field Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_row_width_avg,
    csv_string_field_count,
    csv_max_string_field_length,
)

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvRowWidthAvg:
    def test_return_type(self):
        assert isinstance(csv_row_width_avg(_MINIMAL), (int, float))

    def test_exact_2_for_minimal_2x2(self):
        assert csv_row_width_avg(_MINIMAL) == 2.0

    def test_exact_3_for_quoted_fields(self):
        assert csv_row_width_avg(_QUOTED) == 3.0

    def test_exact_1_for_single_cell(self):
        assert csv_row_width_avg(_SINGLE) == 1.0

    def test_positive(self):
        assert csv_row_width_avg(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert csv_row_width_avg(_MINIMAL) == csv_row_width_avg(_MINIMAL)


class TestCsvStringFieldCount:
    def test_return_type(self):
        assert isinstance(csv_string_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal_2x2(self):
        assert csv_string_field_count(_MINIMAL) == 2

    def test_exact_4_for_quoted_fields(self):
        assert csv_string_field_count(_QUOTED) == 4

    def test_nonnegative(self):
        assert csv_string_field_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_string_field_count(_MINIMAL) == csv_string_field_count(_MINIMAL)


class TestCsvMaxStringFieldLength:
    def test_return_type(self):
        assert isinstance(csv_max_string_field_length(_MINIMAL), int)

    def test_exact_5_for_minimal_2x2(self):
        assert csv_max_string_field_length(_MINIMAL) == 5

    def test_exact_22_for_quoted_fields(self):
        assert csv_max_string_field_length(_QUOTED) == 22

    def test_nonnegative(self):
        assert csv_max_string_field_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert csv_max_string_field_length(_MINIMAL) == csv_max_string_field_length(_MINIMAL)
