"""Tests for 6 new CSV analytics functions.

Covers: csv_numeric_sum, csv_avg_numeric_value, csv_is_single_row,
    csv_empty_column_count, csv_longest_row_index, csv_total_string_length.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import (
    csv_avg_numeric_value,
    csv_empty_column_count,
    csv_is_single_row,
    csv_longest_row_index,
    csv_numeric_sum,
    csv_total_string_length,
)


@pytest.fixture
def multi_csv(tmp_path):
    content = "name,age,score\nalice,30,95.5\nbob,25,80.0\ncarol,35,88.0\n"
    f = tmp_path / "data.csv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def single_row_csv(tmp_path):
    content = "val1,val2,val3\n"
    f = tmp_path / "single.csv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def sparse_csv(tmp_path):
    content = "a,,c\nd,,f\n"
    f = tmp_path / "sparse.csv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def empty_csv(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("", encoding="utf-8")
    return f


class TestCsvNumericSum:
    def test_returns_float(self, multi_csv):
        result = csv_numeric_sum(multi_csv)
        assert isinstance(result, float)

    def test_sums_all_numerics(self, multi_csv):
        result = csv_numeric_sum(multi_csv)
        # age: 30+25+35=90, score: 95.5+80.0+88.0=263.5
        assert result == pytest.approx(353.5, abs=1.0)

    def test_zero_for_empty(self, empty_csv):
        assert csv_numeric_sum(empty_csv) == 0.0

    def test_string_only_zero(self, tmp_path):
        f = tmp_path / "str.csv"
        f.write_text("name,city\nalice,nyc\n", encoding="utf-8")
        assert csv_numeric_sum(f) == 0.0


class TestCsvAvgNumericValue:
    def test_returns_float(self, multi_csv):
        result = csv_avg_numeric_value(multi_csv)
        assert isinstance(result, float)

    def test_positive_for_numeric(self, multi_csv):
        result = csv_avg_numeric_value(multi_csv)
        assert result > 0

    def test_zero_for_empty(self, empty_csv):
        assert csv_avg_numeric_value(empty_csv) == 0.0

    def test_single_value(self, tmp_path):
        f = tmp_path / "one.csv"
        f.write_text("val\n42\n", encoding="utf-8")
        assert csv_avg_numeric_value(f) == pytest.approx(42.0)


class TestCsvIsSingleRow:
    def test_true_for_one_data_row(self, single_row_csv):
        assert csv_is_single_row(single_row_csv) is True

    def test_false_for_multi(self, multi_csv):
        assert csv_is_single_row(multi_csv) is False

    def test_returns_bool(self, single_row_csv):
        assert isinstance(csv_is_single_row(single_row_csv), bool)

    def test_false_for_empty(self, empty_csv):
        assert csv_is_single_row(empty_csv) is False


class TestCsvEmptyColumnCount:
    def test_returns_int(self, multi_csv):
        result = csv_empty_column_count(multi_csv)
        assert isinstance(result, int)

    def test_zero_for_full_data(self, multi_csv):
        assert csv_empty_column_count(multi_csv) == 0

    def test_detects_empty_column(self, sparse_csv):
        result = csv_empty_column_count(sparse_csv)
        assert result >= 1

    def test_zero_for_empty_file(self, empty_csv):
        assert csv_empty_column_count(empty_csv) == 0


class TestCsvLongestRowIndex:
    def test_returns_int(self, multi_csv):
        result = csv_longest_row_index(multi_csv)
        assert isinstance(result, int)

    def test_minus_one_for_empty(self, empty_csv):
        assert csv_longest_row_index(empty_csv) == -1

    def test_nonneg_for_data(self, multi_csv):
        result = csv_longest_row_index(multi_csv)
        assert result >= 0

    def test_valid_index(self, multi_csv):
        result = csv_longest_row_index(multi_csv)
        assert 0 <= result < 3


class TestCsvTotalStringLength:
    def test_returns_int(self, multi_csv):
        result = csv_total_string_length(multi_csv)
        assert isinstance(result, int)

    def test_positive_for_data(self, multi_csv):
        assert csv_total_string_length(multi_csv) > 0

    def test_zero_for_empty(self, empty_csv):
        assert csv_total_string_length(empty_csv) == 0

    def test_grows_with_data(self, tmp_path):
        f1 = tmp_path / "small.csv"
        f1.write_text("a,b\n1,2\n", encoding="utf-8")
        f2 = tmp_path / "large.csv"
        f2.write_text("alpha,beta\nhello,world\n", encoding="utf-8")
        assert csv_total_string_length(f2) > csv_total_string_length(f1)
