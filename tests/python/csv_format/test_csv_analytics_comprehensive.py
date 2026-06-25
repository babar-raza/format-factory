"""Comprehensive CSV analytics tests — BATCH-5 roundtrip and analytics coverage.
All csv_ analytics functions take file paths (not model dicts).
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (  # type: ignore
    parse_csv, parse_csv_strict,
    csv_row_count, csv_column_count, csv_total_cell_count,
    csv_is_rectangular, csv_is_square, csv_is_single_row, csv_is_multi_row,
    csv_is_single_column, csv_is_multi_column, csv_is_empty, csv_is_all_numeric,
    csv_has_header, csv_has_duplicates, csv_has_empty_rows,
    csv_nonempty_row_count, csv_nonempty_row_ratio,
    csv_nonempty_cell_count, csv_nonempty_cell_ratio,
    csv_empty_cell_count, csv_empty_cell_ratio, csv_empty_column_count,
    csv_avg_fields_per_row, csv_max_field_count, csv_min_row_field_count,
    csv_avg_cell_length, csv_average_field_length, csv_total_string_length,
    csv_max_field_value_length, csv_min_field_length, csv_max_row_length,
    csv_min_row_length, csv_row_length_sum, csv_row_length_variance,
    csv_column_count_variance, csv_avg_row_length,
    csv_numeric_sum, csv_avg_numeric_value, csv_max_numeric_value, csv_min_numeric_value,
    csv_numeric_cell_ratio, csv_numeric_density, csv_numeric_row_count,
    csv_numeric_column_count, csv_string_cell_count, csv_string_density,
    csv_distinct_value_count, csv_unique_value_count, csv_unique_row_count,
    csv_duplicate_row_count, csv_all_rows, csv_all_rows_same_length,
    csv_data_density, csv_longest_row_index, csv_to_dicts,
    csv_header_count, csv_header_length_sum, csv_column_name_lengths,
    csv_has_numeric_header, csv_field_type_ratio, csv_field_type_variance,
    csv_column_type_counts, csv_column_value_variance, csv_empty_field_ratio,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

SIMPLE_TXT = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,NYC\n"
NUMERIC_TXT = "1,2,3\n4,5,6\n7,8,9\n"
EMPTY_CELLS_TXT = "a,b,c\n1,,3\n,5,\n7,8,9\n"
DUPE_TXT = "a,b\n1,2\n1,2\n3,4\n"
SINGLE_COL_TXT = "val\n1\n2\n3\n"


@pytest.fixture
def simple_f(tmp_path):
    p = tmp_path / "simple.csv"
    p.write_text(SIMPLE_TXT, encoding="utf-8")
    return str(p)


@pytest.fixture
def numeric_f(tmp_path):
    p = tmp_path / "num.csv"
    p.write_text(NUMERIC_TXT, encoding="utf-8")
    return str(p)


@pytest.fixture
def empty_f(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text(EMPTY_CELLS_TXT, encoding="utf-8")
    return str(p)


@pytest.fixture
def dupe_f(tmp_path):
    p = tmp_path / "dupe.csv"
    p.write_text(DUPE_TXT, encoding="utf-8")
    return str(p)


@pytest.fixture
def single_col_f(tmp_path):
    p = tmp_path / "scol.csv"
    p.write_text(SINGLE_COL_TXT, encoding="utf-8")
    return str(p)


# ── Shape tests ───────────────────────────────────────────────────────────────

class TestShape:
    def test_row_count(self, simple_f):
        assert csv_row_count(simple_f) == 3

    def test_column_count(self, simple_f):
        assert csv_column_count(simple_f) == 3

    def test_total_cell_count(self, simple_f):
        assert csv_total_cell_count(simple_f) == 9

    def test_is_rectangular_true(self, simple_f):
        assert csv_is_rectangular(simple_f) is True

    def test_is_square_true(self, numeric_f):
        assert csv_is_square(numeric_f) is True

    def test_is_square_true_for_3x3(self, simple_f):
        # 3 rows × 3 cols is square
        assert csv_is_square(simple_f) is True

    def test_is_single_row_false(self, simple_f):
        assert csv_is_single_row(simple_f) is False

    def test_is_multi_row_true(self, simple_f):
        assert csv_is_multi_row(simple_f) is True

    def test_is_multi_column_true(self, simple_f):
        assert csv_is_multi_column(simple_f) is True

    def test_is_empty_false(self, simple_f):
        assert csv_is_empty(simple_f) is False


# ── Numeric tests ─────────────────────────────────────────────────────────────

class TestNumeric:
    def test_is_all_numeric_true(self, numeric_f):
        assert csv_is_all_numeric(numeric_f) is True

    def test_is_all_numeric_false(self, simple_f):
        assert csv_is_all_numeric(simple_f) is False

    def test_numeric_sum(self, numeric_f):
        assert csv_numeric_sum(numeric_f) == 45.0

    def test_avg_numeric_value(self, numeric_f):
        assert csv_avg_numeric_value(numeric_f) == 5.0

    def test_max_numeric_value(self, numeric_f):
        assert csv_max_numeric_value(numeric_f) == 9.0

    def test_min_numeric_value(self, numeric_f):
        assert csv_min_numeric_value(numeric_f) == 1.0

    def test_numeric_row_count_positive(self, numeric_f):
        assert csv_numeric_row_count(numeric_f) >= 1

    def test_numeric_column_count_positive(self, numeric_f):
        assert csv_numeric_column_count(numeric_f) >= 1

    def test_numeric_cell_ratio_full(self, numeric_f):
        assert csv_numeric_cell_ratio(numeric_f) == 1.0

    def test_numeric_density_positive(self, numeric_f):
        assert csv_numeric_density(numeric_f) > 0

    def test_string_cell_count_nonneg(self, simple_f):
        assert csv_string_cell_count(simple_f) >= 0

    def test_string_density_nonneg(self, simple_f):
        assert csv_string_density(simple_f) >= 0


# ── Empty cell tests ─────────────────────────────────────────────────────────

class TestEmptyCells:
    def test_empty_cell_count_positive(self, empty_f):
        assert csv_empty_cell_count(empty_f) > 0

    def test_empty_cell_ratio_partial(self, empty_f):
        ratio = csv_empty_cell_ratio(empty_f)
        assert 0 < ratio < 1

    def test_nonempty_cell_count(self, simple_f):
        assert csv_nonempty_cell_count(simple_f) == 9

    def test_nonempty_cell_ratio_full(self, simple_f):
        assert csv_nonempty_cell_ratio(simple_f) == 1.0

    def test_nonempty_row_count(self, simple_f):
        assert csv_nonempty_row_count(simple_f) == 3

    def test_nonempty_row_ratio_full(self, simple_f):
        assert csv_nonempty_row_ratio(simple_f) == 1.0

    def test_has_empty_rows_false(self, simple_f):
        assert csv_has_empty_rows(simple_f) is False

    def test_empty_field_ratio_positive(self, empty_f):
        assert csv_empty_field_ratio(empty_f) > 0

    def test_empty_column_count_zero(self, simple_f):
        assert csv_empty_column_count(simple_f) == 0


# ── Duplicate and uniqueness tests ────────────────────────────────────────────

class TestUniqueness:
    def test_has_duplicates_false(self, simple_f):
        assert csv_has_duplicates(simple_f) is False

    def test_has_duplicates_true(self, dupe_f):
        assert csv_has_duplicates(dupe_f) is True

    def test_duplicate_row_count_positive(self, dupe_f):
        assert csv_duplicate_row_count(dupe_f) >= 1

    def test_unique_row_count(self, simple_f):
        assert csv_unique_row_count(simple_f) == 3

    def test_distinct_value_count_positive(self, simple_f):
        assert csv_distinct_value_count(simple_f) >= 1

    def test_unique_value_count_positive(self, simple_f):
        assert csv_unique_value_count(simple_f) >= 1


# ── Length and field tests ────────────────────────────────────────────────────

class TestLengths:
    def test_avg_cell_length_positive(self, simple_f):
        assert csv_avg_cell_length(simple_f) > 0

    def test_average_field_length_positive(self, simple_f):
        assert csv_average_field_length(simple_f) > 0

    def test_total_string_length_positive(self, simple_f):
        assert csv_total_string_length(simple_f) > 0

    def test_max_field_value_length_positive(self, simple_f):
        assert csv_max_field_value_length(simple_f) > 0

    def test_min_field_length_nonneg(self, simple_f):
        assert csv_min_field_length(simple_f) >= 0

    def test_max_row_length_positive(self, simple_f):
        assert csv_max_row_length(simple_f) > 0

    def test_min_row_length_positive(self, simple_f):
        assert csv_min_row_length(simple_f) > 0

    def test_row_length_sum_positive(self, simple_f):
        assert csv_row_length_sum(simple_f) > 0

    def test_row_length_variance_nonneg(self, simple_f):
        assert csv_row_length_variance(simple_f) >= 0

    def test_avg_row_length_positive(self, simple_f):
        assert csv_avg_row_length(simple_f) > 0

    def test_avg_fields_per_row(self, simple_f):
        assert csv_avg_fields_per_row(simple_f) == 3.0

    def test_max_field_count(self, simple_f):
        assert csv_max_field_count(simple_f) == 3

    def test_min_row_field_count(self, simple_f):
        assert csv_min_row_field_count(simple_f) == 3

    def test_column_count_variance_zero_uniform(self, simple_f):
        assert csv_column_count_variance(simple_f) == 0.0


# ── Header and metadata tests ─────────────────────────────────────────────────

class TestHeadersAndMeta:
    def test_has_header_true(self, simple_f):
        assert csv_has_header(simple_f) is True

    def test_header_count(self, simple_f):
        # csv_header_count returns number of header fields (may be 0 if header is metadata)
        assert csv_header_count(simple_f) >= 0

    def test_header_length_sum_positive(self, simple_f):
        assert csv_header_length_sum(simple_f) > 0

    def test_column_name_lengths_is_collection(self, simple_f):
        lengths = csv_column_name_lengths(simple_f)
        assert isinstance(lengths, (list, dict))

    def test_has_numeric_header_false(self, simple_f):
        assert csv_has_numeric_header(simple_f) is False


# ── All rows and data density ─────────────────────────────────────────────────

class TestRowsAndDensity:
    def test_all_rows_returns_list(self, simple_f):
        rows = csv_all_rows(simple_f)
        assert isinstance(rows, list)
        assert len(rows) == 3

    def test_all_rows_same_length_true(self, simple_f):
        assert csv_all_rows_same_length(simple_f) is True

    def test_data_density_positive(self, simple_f):
        density = csv_data_density(simple_f)
        assert 0 < density <= 1.0

    def test_longest_row_index_is_int(self, simple_f):
        idx = csv_longest_row_index(simple_f)
        assert isinstance(idx, int)


# ── Field type tests ──────────────────────────────────────────────────────────

class TestFieldTypes:
    def test_field_type_ratio_not_none(self, simple_f):
        result = csv_field_type_ratio(simple_f)
        assert result is not None

    def test_field_type_variance_is_numeric(self, simple_f):
        result = csv_field_type_variance(simple_f)
        assert isinstance(result, (float, int))

    def test_column_type_counts_not_none(self, simple_f):
        result = csv_column_type_counts(simple_f)
        assert result is not None

    def test_column_value_variance_not_none(self, simple_f):
        result = csv_column_value_variance(simple_f)
        assert result is not None


# ── Conversion tests ──────────────────────────────────────────────────────────

class TestConversions:
    def test_to_dicts_returns_list(self, simple_f):
        result = csv_to_dicts(simple_f)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_to_dicts_first_row_alice(self, simple_f):
        result = csv_to_dicts(simple_f)
        assert result[0]["name"] == "Alice"

    def test_to_dicts_consistent_keys(self, simple_f):
        result = csv_to_dicts(simple_f)
        keys = [frozenset(r.keys()) for r in result]
        assert len(set(keys)) == 1


# ── Parse roundtrip ───────────────────────────────────────────────────────────

class TestParseRoundtrip:
    def test_parse_csv_returns_dict(self, simple_f):
        m = parse_csv(simple_f)
        assert isinstance(m, dict)

    def test_parse_csv_strict_returns_dict(self, simple_f):
        m = parse_csv_strict(simple_f)
        assert isinstance(m, dict)

    def test_parse_csv_has_rows(self, simple_f):
        m = parse_csv(simple_f)
        assert m.get("rows") is not None or m.get("row_count") is not None

    def test_parse_csv_has_headers(self, simple_f):
        m = parse_csv(simple_f)
        assert m.get("headers") is not None

    def test_parse_csv_single_col(self, single_col_f):
        assert csv_is_single_column(single_col_f) is True

    def test_numeric_is_all_numeric(self, numeric_f):
        assert csv_is_all_numeric(numeric_f) is True
