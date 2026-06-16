"""Tests for 6 new TSV analytics functions.

Covers: tsv_numeric_sum, tsv_avg_numeric_value, tsv_has_duplicates,
    tsv_empty_column_count, tsv_is_single_row, tsv_longest_row_index.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv import (
    tsv_avg_numeric_value,
    tsv_empty_column_count,
    tsv_has_duplicates,
    tsv_is_single_row,
    tsv_longest_row_index,
    tsv_numeric_sum,
)


@pytest.fixture
def multi_tsv(tmp_path):
    content = "name\tage\tscore\nalice\t30\t95.5\nbob\t25\t80.0\ncarol\t35\t88.0\n"
    f = tmp_path / "data.tsv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def single_row_tsv(tmp_path):
    content = "col1\tcol2\tcol3\n"
    f = tmp_path / "single.tsv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def dup_tsv(tmp_path):
    content = "col1\tcol2\nfoo\tbar\nfoo\tbar\nbaz\tqux\n"
    f = tmp_path / "dup.tsv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def sparse_tsv(tmp_path):
    content = "a\t\tc\nd\t\tf\n"
    f = tmp_path / "sparse.tsv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def empty_tsv(tmp_path):
    f = tmp_path / "empty.tsv"
    f.write_text("", encoding="utf-8")
    return f


class TestTsvNumericSum:
    def test_returns_float(self, multi_tsv):
        result = tsv_numeric_sum(multi_tsv)
        assert isinstance(result, float)

    def test_sums_numeric_values(self, multi_tsv):
        result = tsv_numeric_sum(multi_tsv)
        # age: 30+25+35=90, score: 95.5+80.0+88.0=263.5
        assert result == pytest.approx(353.5, abs=1.0)

    def test_zero_for_empty(self, empty_tsv):
        assert tsv_numeric_sum(empty_tsv) == 0.0

    def test_string_only_returns_zero(self, tmp_path):
        f = tmp_path / "str.tsv"
        f.write_text("a\tb\nc\td\n", encoding="utf-8")
        assert tsv_numeric_sum(f) == 0.0


class TestTsvAvgNumericValue:
    def test_returns_float(self, multi_tsv):
        result = tsv_avg_numeric_value(multi_tsv)
        assert isinstance(result, float)

    def test_positive_for_numeric_data(self, multi_tsv):
        result = tsv_avg_numeric_value(multi_tsv)
        assert result > 0

    def test_zero_for_empty(self, empty_tsv):
        assert tsv_avg_numeric_value(empty_tsv) == 0.0

    def test_zero_for_no_numeric(self, tmp_path):
        f = tmp_path / "str.tsv"
        f.write_text("hello\tworld\n", encoding="utf-8")
        assert tsv_avg_numeric_value(f) == 0.0

    def test_single_value(self, tmp_path):
        f = tmp_path / "one.tsv"
        f.write_text("42\n", encoding="utf-8")
        assert tsv_avg_numeric_value(f) == pytest.approx(42.0)


class TestTsvHasDuplicates:
    def test_true_for_dup(self, dup_tsv):
        assert tsv_has_duplicates(dup_tsv) is True

    def test_false_for_no_dup(self, multi_tsv):
        assert tsv_has_duplicates(multi_tsv) is False

    def test_returns_bool(self, multi_tsv):
        assert isinstance(tsv_has_duplicates(multi_tsv), bool)

    def test_false_for_empty(self, empty_tsv):
        assert tsv_has_duplicates(empty_tsv) is False


class TestTsvEmptyColumnCount:
    def test_returns_int(self, multi_tsv):
        result = tsv_empty_column_count(multi_tsv)
        assert isinstance(result, int)

    def test_zero_for_full_data(self, multi_tsv):
        assert tsv_empty_column_count(multi_tsv) == 0

    def test_counts_empty_column(self, sparse_tsv):
        result = tsv_empty_column_count(sparse_tsv)
        assert result >= 1

    def test_zero_for_empty_file(self, empty_tsv):
        assert tsv_empty_column_count(empty_tsv) == 0


class TestTsvIsSingleRow:
    def test_true_for_single_row(self, single_row_tsv):
        assert tsv_is_single_row(single_row_tsv) is True

    def test_false_for_multi_row(self, multi_tsv):
        assert tsv_is_single_row(multi_tsv) is False

    def test_returns_bool(self, single_row_tsv):
        assert isinstance(tsv_is_single_row(single_row_tsv), bool)

    def test_false_for_empty(self, empty_tsv):
        assert tsv_is_single_row(empty_tsv) is False


class TestTsvLongestRowIndex:
    def test_returns_int(self, multi_tsv):
        result = tsv_longest_row_index(multi_tsv)
        assert isinstance(result, int)

    def test_minus_one_for_empty(self, empty_tsv):
        assert tsv_longest_row_index(empty_tsv) == -1

    def test_nonnegative_for_data(self, multi_tsv):
        result = tsv_longest_row_index(multi_tsv)
        assert result >= 0

    def test_valid_index_range(self, multi_tsv):
        result = tsv_longest_row_index(multi_tsv)
        assert 0 <= result < 4
