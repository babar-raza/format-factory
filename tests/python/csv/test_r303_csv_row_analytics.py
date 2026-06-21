"""Tests for csv_is_single_row and csv_total_field_length_sum (Sprint r303)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_is_single_row, csv_total_field_length_sum

_CSV = _REPO / "samples" / "by-format" / "csv"


class TestCsvIsSingleRow:
    """Tests for csv_is_single_row."""

    def test_minimal_2x2_is_not_single_row(self):
        """minimal-2x2.csv has 2 rows → False."""
        result = csv_is_single_row(_CSV / "minimal-2x2.csv")
        assert result is False

    def test_quoted_fields_is_not_single_row(self):
        """quoted-fields.csv has 2 rows → False."""
        result = csv_is_single_row(_CSV / "quoted-fields.csv")
        assert result is False

    def test_single_cell_is_single_row(self):
        """single-cell.csv has 1 row → True."""
        result = csv_is_single_row(_CSV / "single-cell.csv")
        assert result is True

    def test_returns_bool(self):
        result = csv_is_single_row(_CSV / "single-cell.csv")
        assert isinstance(result, bool)

    def test_multi_row_files_return_false(self):
        for f in ["minimal-2x2.csv", "quoted-fields.csv"]:
            assert csv_is_single_row(_CSV / f) is False

    def test_single_true_minimal_false(self):
        r1 = csv_is_single_row(_CSV / "minimal-2x2.csv")
        r2 = csv_is_single_row(_CSV / "single-cell.csv")
        assert r1 is False and r2 is True


class TestCsvTotalFieldLengthSum:
    """Tests for csv_total_field_length_sum."""

    def test_minimal_2x2_sum_is_12(self):
        """minimal-2x2.csv: 4 fields, total char length = 12."""
        result = csv_total_field_length_sum(_CSV / "minimal-2x2.csv")
        assert result == 12

    def test_quoted_fields_sum_is_61(self):
        """quoted-fields.csv: fields sum = 61."""
        result = csv_total_field_length_sum(_CSV / "quoted-fields.csv")
        assert result == 61

    def test_single_cell_sum_is_2(self):
        """single-cell.csv: 1 field with 2 chars."""
        result = csv_total_field_length_sum(_CSV / "single-cell.csv")
        assert result == 2

    def test_returns_int(self):
        result = csv_total_field_length_sum(_CSV / "single-cell.csv")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-2x2.csv", "quoted-fields.csv", "single-cell.csv"]:
            assert csv_total_field_length_sum(_CSV / f) >= 0

    def test_quoted_larger_than_minimal(self):
        r1 = csv_total_field_length_sum(_CSV / "minimal-2x2.csv")
        r2 = csv_total_field_length_sum(_CSV / "quoted-fields.csv")
        assert r2 > r1
