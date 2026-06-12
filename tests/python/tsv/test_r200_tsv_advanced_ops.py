"""
tests/python/tsv/test_r200_tsv_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT4-001
TASK-002: TSV advanced operations — analytics, filtering, transformation, stats.

Covers: probe_tsv, load_tsv, get_headers, count_rows, column_count, get_column,
get_row, get_row_by_key, get_column_values, sum_column_tsv, average_column_tsv,
min_column_tsv, max_column_tsv, median_column_tsv, std_column_tsv, unique_column_values,
filter_rows, find_rows_containing, sort_rows, sample_rows, deduplicate_rows,
rename_column, drop_column, merge_tsv, to_csv, validate_headers,
tsv_row_count, tsv_numeric_cell_count, tsv_nonempty_cell_count,
tsv_empty_row_count, tsv_max_cell_length, write_tsv.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import tsv
from tsv import (
    probe_tsv, load_tsv, parse_tsv, get_headers,
    count_rows, column_count, get_column, get_row, get_row_by_key,
    get_column_values, sum_column_tsv, average_column_tsv,
    min_column_tsv, max_column_tsv, median_column_tsv, std_column_tsv,
    unique_column_values, filter_rows, find_rows_containing, sort_rows,
    sample_rows, deduplicate_rows, rename_column, drop_column,
    merge_tsv, to_csv, validate_headers,
    tsv_row_count, tsv_numeric_cell_count, tsv_nonempty_cell_count,
    tsv_empty_row_count, tsv_max_cell_length,
    write_tsv, append_row, add_column,
)

_CONTENT = "name\tage\tdept\nAlice\t30\tengineering\nBob\t25\tdesign\nCarol\t35\tengineering\n"


def _make_tsv_file(content=None):
    content = content or _CONTENT
    fd, path = tempfile.mkstemp(suffix=".tsv")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class TestTsvProbeAndLoad:
    """Probe and load functions."""

    def test_probe_tsv_returns_dict(self):
        path = _make_tsv_file()
        try:
            result = probe_tsv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_tsv_has_expected_keys(self):
        path = _make_tsv_file()
        try:
            result = probe_tsv(path)
            assert result.get("exists") is True
            assert "column_count" in result
        finally:
            os.unlink(path)

    def test_load_tsv_returns_dict(self):
        path = _make_tsv_file()
        try:
            result = load_tsv(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_get_headers_returns_list(self):
        path = _make_tsv_file()
        try:
            headers = get_headers(path)
            assert isinstance(headers, list)
            assert "name" in headers
        finally:
            os.unlink(path)

    def test_validate_headers_valid(self):
        path = _make_tsv_file()
        try:
            result = validate_headers(path, ["name", "age", "dept"])
            assert isinstance(result, dict)
            assert result.get("valid") is True
        finally:
            os.unlink(path)

    def test_validate_headers_invalid(self):
        path = _make_tsv_file()
        try:
            result = validate_headers(path, ["name", "salary"])
            assert result.get("valid") is False
        finally:
            os.unlink(path)


class TestTsvRowColCounts:
    """Row/column count functions."""

    def test_count_rows_correct(self):
        path = _make_tsv_file()
        try:
            assert count_rows(path) == 3
        finally:
            os.unlink(path)

    def test_column_count_correct(self):
        path = _make_tsv_file()
        try:
            assert column_count(path) == 3
        finally:
            os.unlink(path)

    def test_tsv_row_count_positive(self):
        path = _make_tsv_file()
        try:
            n = tsv_row_count(path)
            assert isinstance(n, int)
            assert n == 3
        finally:
            os.unlink(path)

    def test_tsv_numeric_cell_count_positive(self):
        path = _make_tsv_file()
        try:
            n = tsv_numeric_cell_count(path)
            assert isinstance(n, int)
            assert n == 3  # age column
        finally:
            os.unlink(path)

    def test_tsv_nonempty_cell_count_positive(self):
        path = _make_tsv_file()
        try:
            n = tsv_nonempty_cell_count(path)
            assert isinstance(n, int)
            assert n == 9  # 3 rows * 3 cols
        finally:
            os.unlink(path)

    def test_tsv_empty_row_count_zero(self):
        path = _make_tsv_file()
        try:
            n = tsv_empty_row_count(path)
            assert isinstance(n, int)
            assert n == 0
        finally:
            os.unlink(path)

    def test_tsv_max_cell_length_positive(self):
        path = _make_tsv_file()
        try:
            n = tsv_max_cell_length(path)
            assert isinstance(n, int)
            assert n > 0
        finally:
            os.unlink(path)


class TestTsvValueAccess:
    """Value access functions."""

    def test_get_column_returns_list(self):
        path = _make_tsv_file()
        try:
            result = get_column(path, "name")
            assert isinstance(result, list)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_get_row_returns_list(self):
        path = _make_tsv_file()
        try:
            result = get_row(path, 0)
            assert isinstance(result, list)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_get_row_by_key_returns_row(self):
        path = _make_tsv_file()
        try:
            result = get_row_by_key(path, "name", "Alice")
            assert isinstance(result, list)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_get_column_values_returns_list(self):
        path = _make_tsv_file()
        try:
            result = get_column_values(path, "name")
            assert isinstance(result, list)
            assert "Bob" in result
        finally:
            os.unlink(path)

    def test_unique_column_values_returns_list(self):
        path = _make_tsv_file()
        try:
            result = unique_column_values(path, "dept")
            assert isinstance(result, list)
            assert "engineering" in result
            assert "design" in result
        finally:
            os.unlink(path)


class TestTsvColumnAnalytics:
    """Numeric column analytics."""

    def test_sum_column_tsv_correct(self):
        path = _make_tsv_file()
        try:
            assert sum_column_tsv(path, "age") == 90.0
        finally:
            os.unlink(path)

    def test_average_column_tsv_correct(self):
        path = _make_tsv_file()
        try:
            assert average_column_tsv(path, "age") == 30.0
        finally:
            os.unlink(path)

    def test_min_column_tsv_correct(self):
        path = _make_tsv_file()
        try:
            assert min_column_tsv(path, "age") == 25.0
        finally:
            os.unlink(path)

    def test_max_column_tsv_correct(self):
        path = _make_tsv_file()
        try:
            assert max_column_tsv(path, "age") == 35.0
        finally:
            os.unlink(path)

    def test_median_column_tsv_correct(self):
        path = _make_tsv_file()
        try:
            result = median_column_tsv(path, "age")
            assert isinstance(result, float)
            assert result == 30.0
        finally:
            os.unlink(path)

    def test_std_column_tsv_positive(self):
        path = _make_tsv_file()
        try:
            result = std_column_tsv(path, "age")
            assert isinstance(result, float)
            assert result > 0
        finally:
            os.unlink(path)


class TestTsvFiltering:
    """Filter, search, sort, sample."""

    def test_filter_rows_returns_dict(self):
        path = _make_tsv_file()
        try:
            result = filter_rows(path, "dept", "engineering")
            assert isinstance(result, dict)
            assert result.get("row_count", 0) == 2
        finally:
            os.unlink(path)

    def test_find_rows_containing_returns_list(self):
        path = _make_tsv_file()
        try:
            result = find_rows_containing(path, "Alice")
            assert isinstance(result, list)
            assert 0 in result
        finally:
            os.unlink(path)

    def test_sort_rows_ascending(self):
        path = _make_tsv_file()
        try:
            result = sort_rows(path, "age")
            assert isinstance(result, dict)
            rows = result.get("rows", [])
            if rows:
                ages = [int(r[1]) for r in rows]
                assert ages == sorted(ages)
        finally:
            os.unlink(path)

    def test_sample_rows_returns_subset(self):
        path = _make_tsv_file()
        try:
            result = sample_rows(path, 2)
            assert isinstance(result, dict)
            rows = result.get("rows", [])
            assert len(rows) <= 2
        finally:
            os.unlink(path)

    def test_deduplicate_rows_returns_list(self):
        path = _make_tsv_file()
        try:
            result = deduplicate_rows(path)
            assert isinstance(result, list)
        finally:
            os.unlink(path)


class TestTsvTransformation:
    """rename_column, drop_column, merge_tsv, to_csv."""

    def test_rename_column_changes_header(self):
        path = _make_tsv_file()
        try:
            result = rename_column(path, "name", "full_name")
            assert isinstance(result, dict)
            assert "full_name" in result.get("headers", [])
        finally:
            os.unlink(path)

    def test_drop_column_removes_column(self):
        path = _make_tsv_file()
        try:
            result = drop_column(path, "dept")
            assert isinstance(result, dict)
            assert "dept" not in result.get("headers", [])
        finally:
            os.unlink(path)

    def test_merge_tsv_combines_rows(self):
        path_a = _make_tsv_file()
        path_b = _make_tsv_file("name\tage\tdept\nDan\t40\thr\n")
        try:
            result = merge_tsv(path_a, path_b)
            assert isinstance(result, dict)
            assert result.get("row_count", 0) == 4
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_to_csv_returns_string(self):
        path = _make_tsv_file()
        try:
            result = to_csv(path)
            assert isinstance(result, str)
            assert "name" in result
        finally:
            os.unlink(path)


class TestTsvWriteAndAppend:
    """write_tsv, append_row, add_column."""

    def test_write_tsv_produces_file(self):
        path = _make_tsv_file()
        fd, out = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        try:
            data = load_tsv(path)
            write_tsv(data, out)
            assert os.path.getsize(out) > 0
        finally:
            os.unlink(path)
            os.unlink(out)

    def test_append_row_appends_to_file(self):
        # append_row(file_path, row) appends in-place and returns None
        path = _make_tsv_file()
        try:
            size_before = os.path.getsize(path)
            result = append_row(path, ["Dan", "40", "hr"])
            size_after = os.path.getsize(path)
            assert result is None  # returns None
            assert size_after > size_before
        finally:
            os.unlink(path)

    def test_add_column_adds_header(self):
        # add_column(path, col_name, values) takes file path
        path = _make_tsv_file()
        try:
            result = add_column(path, "status", ["active", "active", "active"])
            assert isinstance(result, dict)
            assert "status" in result.get("headers", [])
        finally:
            os.unlink(path)
