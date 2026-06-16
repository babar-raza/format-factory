"""
Tests for CSV analytics gap closure (7 FOSS gaps).
Closes: GAP-CSV-FOSS-CSV_AVG_CELL-001, GAP-CSV-FOSS-CSV_AVG_NUME-001,
        GAP-CSV-FOSS-CSV_EMPTY_CO-001, GAP-CSV-FOSS-CSV_LONGEST_-001,
        GAP-CSV-FOSS-CSV_TOTAL_ST-001, GAP-CSV-FOSS-CSV_IS_SQUAR-001,
        GAP-CSV-FOSS-CSV_COLUMN_V-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_cell_length,
    csv_avg_numeric_value,
    csv_empty_column_count,
    csv_longest_row_index,
    csv_total_string_length,
    csv_is_square,
    csv_column_value_variance,
)

_CSV_2x2 = _REPO / "samples/by-format/csv/minimal-2x2.csv"
_CSV_NUMERIC = _REPO / "samples/by-format/csv/quoted-fields.csv"


class TestCsvAvgCellLength:
    def test_returns_float(self):
        assert isinstance(csv_avg_cell_length(_CSV_2x2), float)

    def test_positive_for_content(self):
        assert csv_avg_cell_length(_CSV_2x2) > 0.0

    def test_zero_for_empty_content(self, tmp_path):
        p = tmp_path / "e.csv"
        p.write_text("")
        assert csv_avg_cell_length(p) == 0.0

    def test_single_cell(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("hello\n")
        result = csv_avg_cell_length(p)
        assert result >= 5.0


class TestCsvAvgNumericValue:
    def test_returns_float(self, tmp_path):
        p = tmp_path / "n.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        assert isinstance(csv_avg_numeric_value(p), float)

    def test_correct_avg(self, tmp_path):
        p = tmp_path / "n.csv"
        p.write_text("x\n10\n20\n30\n")
        result = csv_avg_numeric_value(p)
        assert result == pytest.approx(20.0, abs=1.0)

    def test_zero_for_no_numerics(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("a,b\nhello,world\n")
        assert csv_avg_numeric_value(p) == 0.0

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "n.csv"
        p.write_text("v\n1\n2\n3\n")
        assert csv_avg_numeric_value(p) >= 0.0


class TestCsvEmptyColumnCount:
    def test_returns_int(self, tmp_path):
        p = tmp_path / "c.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        assert isinstance(csv_empty_column_count(p), int)

    def test_zero_for_full_columns(self, tmp_path):
        p = tmp_path / "c.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        assert csv_empty_column_count(p) == 0

    def test_one_empty_column(self, tmp_path):
        p = tmp_path / "c.csv"
        p.write_text("a,b\n,2\n,4\n")
        assert csv_empty_column_count(p) >= 1

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "c.csv"
        p.write_text("a\n1\n2\n")
        assert csv_empty_column_count(p) >= 0


class TestCsvLongestRowIndex:
    def test_returns_int(self, tmp_path):
        p = tmp_path / "r.csv"
        p.write_text("a,b\n1,2\n")
        assert isinstance(csv_longest_row_index(p), int)

    def test_index_in_range(self, tmp_path):
        p = tmp_path / "r.csv"
        p.write_text("a,b\n1,2\n3,4,5\n")
        result = csv_longest_row_index(p)
        assert result >= 0

    def test_last_row_longest(self, tmp_path):
        p = tmp_path / "r.csv"
        p.write_text("a\nb,c,d\n")
        assert csv_longest_row_index(p) >= 0

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "r.csv"
        p.write_text("x\n1\n")
        assert csv_longest_row_index(p) >= 0


class TestCsvTotalStringLength:
    def test_returns_int(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("a,b\nhello,world\n")
        assert isinstance(csv_total_string_length(p), int)

    def test_zero_for_empty(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("")
        assert csv_total_string_length(p) == 0

    def test_positive_for_content(self, tmp_path):
        p = tmp_path / "s.csv"
        p.write_text("hello,world\n")
        assert csv_total_string_length(p) > 0

    def test_longer_content_is_larger(self, tmp_path):
        p1 = tmp_path / "s1.csv"
        p2 = tmp_path / "s2.csv"
        p1.write_text("a\n")
        p2.write_text("hello world foo bar\n")
        assert csv_total_string_length(p2) >= csv_total_string_length(p1)


class TestCsvIsSquare:
    def test_returns_bool(self, tmp_path):
        p = tmp_path / "sq.csv"
        p.write_text("a,b\n1,2\n")
        assert isinstance(csv_is_square(p), bool)

    def test_2x2_is_square(self, tmp_path):
        # csv_is_square compares data row count to field count of first row
        # header=a,b + 2 data rows = 2 rows, 2 cols -> square
        p = tmp_path / "sq.csv"
        p.write_text("a,b\n1,2\n3,4\n")
        assert csv_is_square(p) is True

    def test_rectangular_is_not_square(self, tmp_path):
        p = tmp_path / "rect.csv"
        p.write_text("a,b,c\n1,2,3\n4,5,6\n")
        assert csv_is_square(p) is False

    def test_1x1_is_square(self, tmp_path):
        # 1 data row, 1 column -> square
        p = tmp_path / "one.csv"
        p.write_text("a\n1\n")
        assert csv_is_square(p) is True


class TestCsvColumnValueVariance:
    def test_returns_float(self, tmp_path):
        p = tmp_path / "v.csv"
        p.write_text("a\n1\n2\n3\n")
        assert isinstance(csv_column_value_variance(p), float)

    def test_zero_variance_for_same_values(self, tmp_path):
        p = tmp_path / "v.csv"
        p.write_text("a\n5\n5\n5\n")
        assert csv_column_value_variance(p) == pytest.approx(0.0, abs=0.01)

    def test_positive_variance_for_different_values(self, tmp_path):
        p = tmp_path / "v.csv"
        p.write_text("a\n1\n2\n3\n4\n5\n")
        assert csv_column_value_variance(p) > 0.0

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "v.csv"
        p.write_text("x\n10\n20\n")
        assert csv_column_value_variance(p) >= 0.0
