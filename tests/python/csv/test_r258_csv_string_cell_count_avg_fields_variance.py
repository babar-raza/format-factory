"""Tests for CSV gap closure batch 2 (Sprint 40).

Closes:
  GAP-CSV-FOSS-CSV_STRING_C-001   (Csv String Cell Count)
  GAP-CSV-FOSS-CSV_AVG_FIEL-001   (Csv Avg Fields Per Row)
  GAP-CSV-FOSS-CSV_FIELD_CO-001   (Csv Field Count Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_fields_per_row,
    csv_field_count_variance,
    csv_string_cell_count,
)

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE_CELL = str(_DIR / "single-cell.csv")


class TestCsvStringCellCount:
    def test_return_type(self):
        assert isinstance(csv_string_cell_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert csv_string_cell_count(_MINIMAL_2X2) == 2

    def test_exact_4_for_quoted(self):
        assert csv_string_cell_count(_QUOTED) == 4

    def test_zero_for_single_numeric_cell(self):
        assert csv_string_cell_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert csv_string_cell_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_string_cell_count(_MINIMAL_2X2) == csv_string_cell_count(_MINIMAL_2X2)


class TestCsvAvgFieldsPerRow:
    def test_return_type(self):
        assert isinstance(csv_avg_fields_per_row(_MINIMAL_2X2), float)

    def test_exact_2_0_for_minimal_2x2(self):
        assert csv_avg_fields_per_row(_MINIMAL_2X2) == 2.0

    def test_exact_3_0_for_quoted(self):
        assert csv_avg_fields_per_row(_QUOTED) == 3.0

    def test_exact_1_0_for_single_cell(self):
        assert csv_avg_fields_per_row(_SINGLE_CELL) == 1.0

    def test_positive(self):
        assert csv_avg_fields_per_row(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_avg_fields_per_row(_MINIMAL_2X2) == csv_avg_fields_per_row(_MINIMAL_2X2)


class TestCsvFieldCountVariance:
    def test_return_type(self):
        assert isinstance(csv_field_count_variance(_MINIMAL_2X2), float)

    def test_zero_for_minimal_2x2(self):
        # all rows same field count
        assert csv_field_count_variance(_MINIMAL_2X2) == 0.0

    def test_zero_for_quoted(self):
        assert csv_field_count_variance(_QUOTED) == 0.0

    def test_zero_for_single_cell(self):
        assert csv_field_count_variance(_SINGLE_CELL) == 0.0

    def test_nonnegative(self):
        assert csv_field_count_variance(_MINIMAL_2X2) >= 0.0

    def test_consistent_across_calls(self):
        assert csv_field_count_variance(_MINIMAL_2X2) == csv_field_count_variance(_MINIMAL_2X2)
