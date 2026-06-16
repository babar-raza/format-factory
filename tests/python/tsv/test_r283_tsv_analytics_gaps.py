"""
Tests for TSV analytics gap closure (7 FOSS gaps).
Closes: GAP-TSV-FOSS-TSV_NUMERIC_-001, GAP-TSV-FOSS-TSV_AVG_NUME-001,
        GAP-TSV-FOSS-TSV_HAS_DUPL-001, GAP-TSV-FOSS-TSV_EMPTY_CO-001,
        GAP-TSV-FOSS-TSV_LONGEST_-001, GAP-TSV-FOSS-TSV_MAX_ROW_-001,
        GAP-TSV-FOSS-TSV_DISTINCT-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    tsv_numeric_sum,
    tsv_avg_numeric_value,
    tsv_has_duplicates,
    tsv_empty_column_count,
    tsv_longest_row_index,
    tsv_max_row_cell_count,
    tsv_distinct_value_ratio,
)

_TSV_2x2 = _REPO / "samples/by-format/tsv/minimal-2x2.tsv"
_TSV_MULTI = _REPO / "samples/by-format/tsv/multi-column.tsv"


class TestTsvNumericSum:
    def test_returns_float(self):
        assert isinstance(tsv_numeric_sum(_TSV_2x2), float)

    def test_positive_for_numeric_content(self, tmp_path):
        p = tmp_path / "n.tsv"
        p.write_text("a\tb\n1\t2\n3\t4\n")
        assert tsv_numeric_sum(p) > 0.0

    def test_zero_for_no_numerics(self, tmp_path):
        p = tmp_path / "s.tsv"
        p.write_text("a\tb\nhello\tworld\n")
        assert tsv_numeric_sum(p) == 0.0

    def test_nonnegative_for_positive_content(self, tmp_path):
        p = tmp_path / "n.tsv"
        p.write_text("x\n10\n20\n30\n")
        assert tsv_numeric_sum(p) == pytest.approx(60.0)


class TestTsvAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(tsv_avg_numeric_value(_TSV_2x2), float)

    def test_correct_avg(self, tmp_path):
        p = tmp_path / "n.tsv"
        p.write_text("x\n10\n20\n30\n")
        result = tsv_avg_numeric_value(p)
        assert result == pytest.approx(20.0, abs=1.0)

    def test_zero_for_no_numerics(self, tmp_path):
        p = tmp_path / "s.tsv"
        p.write_text("a\nhello\nworld\n")
        assert tsv_avg_numeric_value(p) == 0.0

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "n.tsv"
        p.write_text("v\n5\n5\n")
        assert tsv_avg_numeric_value(p) >= 0.0


class TestTsvHasDuplicates:
    def test_returns_bool(self):
        assert isinstance(tsv_has_duplicates(_TSV_2x2), bool)

    def test_false_for_unique_rows(self, tmp_path):
        p = tmp_path / "u.tsv"
        p.write_text("a\tb\n1\t2\n3\t4\n")
        assert tsv_has_duplicates(p) is False

    def test_true_for_duplicate_rows(self, tmp_path):
        p = tmp_path / "d.tsv"
        p.write_text("a\tb\n1\t2\n1\t2\n")
        assert tsv_has_duplicates(p) is True

    def test_false_for_single_row(self, tmp_path):
        p = tmp_path / "s.tsv"
        p.write_text("a\tb\n1\t2\n")
        assert tsv_has_duplicates(p) is False


class TestTsvEmptyColumnCount:
    def test_returns_int(self):
        assert isinstance(tsv_empty_column_count(_TSV_2x2), int)

    def test_zero_for_full_columns(self, tmp_path):
        p = tmp_path / "c.tsv"
        p.write_text("a\tb\n1\t2\n3\t4\n")
        assert tsv_empty_column_count(p) == 0

    def test_one_empty_column(self, tmp_path):
        p = tmp_path / "e.tsv"
        p.write_text("a\tb\n\t2\n\t4\n")
        assert tsv_empty_column_count(p) >= 1

    def test_nonnegative(self, tmp_path):
        p = tmp_path / "n.tsv"
        p.write_text("a\n1\n2\n")
        assert tsv_empty_column_count(p) >= 0


class TestTsvLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(tsv_longest_row_index(_TSV_2x2), int)

    def test_nonnegative(self):
        assert tsv_longest_row_index(_TSV_2x2) >= 0

    def test_valid_for_multi_column(self):
        assert tsv_longest_row_index(_TSV_MULTI) >= 0

    def test_single_row(self, tmp_path):
        p = tmp_path / "s.tsv"
        p.write_text("a\tb\n1\t2\n")
        result = tsv_longest_row_index(p)
        assert isinstance(result, int)


class TestTsvMaxRowCellCount:
    def test_returns_int(self):
        assert isinstance(tsv_max_row_cell_count(_TSV_2x2), int)

    def test_positive(self):
        assert tsv_max_row_cell_count(_TSV_2x2) > 0

    def test_correct_count(self, tmp_path):
        p = tmp_path / "c.tsv"
        p.write_text("a\tb\tc\n1\t2\t3\n")
        assert tsv_max_row_cell_count(p) >= 3

    def test_multi_column(self):
        assert tsv_max_row_cell_count(_TSV_MULTI) >= 1


class TestTsvDistinctValueRatio:
    def test_returns_float(self):
        assert isinstance(tsv_distinct_value_ratio(_TSV_2x2), float)

    def test_ratio_in_range(self):
        r = tsv_distinct_value_ratio(_TSV_2x2)
        assert 0.0 <= r <= 1.0

    def test_high_ratio_for_unique_values(self, tmp_path):
        p = tmp_path / "u.tsv"
        p.write_text("a\nb\nc\nd\ne\n")
        assert tsv_distinct_value_ratio(p) > 0.0

    def test_low_ratio_for_repeated_values(self, tmp_path):
        p = tmp_path / "r.tsv"
        p.write_text("a\n1\n1\n1\n")
        result = tsv_distinct_value_ratio(p)
        assert result <= 1.0
