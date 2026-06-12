"""
tests/python/dif/test_r199_dif_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT2-001
TASK-010: DIF advanced operations — analytics, stats, mutation, sort.

Covers: probe_dif, get_title, get_row_count, get_column_count, count_nonempty_cells,
total_cell_count, get_all_values, sum_column, average_column, min/max_column_value,
get_row_values, get_row_as_dict, get_header_info, sort_rows_by_column,
count_distinct_values, filter_rows_by_value, dif_stats, dif_numeric_range,
dif_total_numeric_count, dif_nonempty_row_count, dif_max_row_length,
dif_string_row_count, dif_string_value_list, set_cell_value, add_row, delete_row.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import dif
from dif import (
    parse_dif, parse_dif_strict, probe_dif,
    get_title, get_row_count, get_column_count,
    count_nonempty_cells, total_cell_count,
    get_all_values, sum_column, average_column,
    min_column_value, max_column_value,
    get_row_values, get_row_as_dict, get_header_info,
    sort_rows_by_column, count_distinct_values,
    filter_rows_by_value,
    dif_stats, dif_numeric_range, dif_total_numeric_count,
    dif_nonempty_row_count, dif_max_row_length, dif_string_row_count,
    dif_string_value_list, set_cell_value, add_row, delete_row,
    write_dif, DifDocument, DifCell,
)

_NUMERIC = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif")
_MINIMAL = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif")
_SINGLE = str(_REPO / "samples" / "by-format" / "dif" / "valid" / "single-cell.dif")


class TestDifProbeAndMetadata:
    """Probe and structural metadata (file path based)."""

    def test_probe_dif_returns_dict(self):
        result = probe_dif(_NUMERIC)
        assert isinstance(result, dict)

    def test_probe_dif_valid_header(self):
        result = probe_dif(_NUMERIC)
        assert result.get("valid_header") is True

    def test_probe_dif_has_title(self):
        result = probe_dif(_NUMERIC)
        assert "title" in result

    def test_get_title_returns_string(self):
        title = get_title(_NUMERIC)
        assert isinstance(title, str)
        assert len(title) > 0

    def test_get_row_count_positive(self):
        n = get_row_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_get_column_count_positive(self):
        n = get_column_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_get_header_info_returns_dict(self):
        info = get_header_info(_NUMERIC)
        assert isinstance(info, dict)
        assert "title" in info
        assert "vectors" in info

    def test_get_header_info_counts_match(self):
        info = get_header_info(_NUMERIC)
        assert info["vectors"] == get_column_count(_NUMERIC)


class TestDifValueAccess:
    """Cell and row value access (file path based)."""

    def test_get_all_values_returns_list(self):
        vals = get_all_values(_NUMERIC)
        assert isinstance(vals, list)
        assert len(vals) > 0

    def test_get_all_values_numeric(self):
        vals = get_all_values(_NUMERIC)
        assert all(isinstance(v, (int, float)) for v in vals)

    def test_get_row_values_returns_list(self):
        row = get_row_values(_NUMERIC, 0)
        assert isinstance(row, list)
        assert len(row) > 0

    def test_get_row_as_dict_returns_dict(self):
        doc = parse_dif_strict(_NUMERIC)
        d = get_row_as_dict(doc, 0)
        assert isinstance(d, dict)

    def test_get_row_as_dict_indexed_by_col(self):
        doc = parse_dif_strict(_NUMERIC)
        d = get_row_as_dict(doc, 0)
        assert 0 in d

    def test_count_nonempty_cells_positive(self):
        n = count_nonempty_cells(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_total_cell_count_positive(self):
        n = total_cell_count(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0


class TestDifColumnAnalytics:
    """Column-level analytics (file path based)."""

    def test_sum_column_returns_number(self):
        result = sum_column(_NUMERIC, 0)
        assert isinstance(result, (int, float))

    def test_average_column_returns_number(self):
        result = average_column(_NUMERIC, 0)
        assert isinstance(result, (int, float))

    def test_min_column_value_returns_number(self):
        result = min_column_value(_NUMERIC, 0)
        assert isinstance(result, (int, float))

    def test_max_column_value_returns_number(self):
        result = max_column_value(_NUMERIC, 0)
        assert isinstance(result, (int, float))

    def test_min_lte_max(self):
        assert min_column_value(_NUMERIC, 0) <= max_column_value(_NUMERIC, 0)

    def test_count_distinct_values_int(self):
        n = count_distinct_values(_NUMERIC, 0)
        assert isinstance(n, int)
        assert n >= 1


class TestDifStats:
    """Model-based stats functions (take parse_dif dict)."""

    def test_dif_stats_returns_dict(self):
        doc = parse_dif(_NUMERIC)
        result = dif_stats(doc)
        assert isinstance(result, dict)

    def test_dif_stats_has_row_count(self):
        doc = parse_dif(_NUMERIC)
        result = dif_stats(doc)
        assert "row_count" in result
        assert result["row_count"] >= 1

    def test_dif_stats_has_numeric_cells(self):
        doc = parse_dif(_NUMERIC)
        result = dif_stats(doc)
        assert "numeric_cells" in result
        assert result["numeric_cells"] > 0

    def test_dif_numeric_range_returns_dict(self):
        doc = parse_dif(_NUMERIC)
        result = dif_numeric_range(doc)
        assert isinstance(result, dict)
        assert "min_value" in result
        assert "max_value" in result

    def test_dif_numeric_range_min_lte_max(self):
        doc = parse_dif(_NUMERIC)
        result = dif_numeric_range(doc)
        assert result["min_value"] <= result["max_value"]

    def test_dif_total_numeric_count_positive(self):
        doc = parse_dif(_NUMERIC)
        n = dif_total_numeric_count(doc)
        assert isinstance(n, int)
        assert n > 0

    def test_dif_string_value_list_returns_list(self):
        doc = parse_dif(_NUMERIC)
        result = dif_string_value_list(doc)
        assert isinstance(result, list)


class TestDifPathStats:
    """Path-based stats functions."""

    def test_dif_nonempty_row_count_positive(self):
        n = dif_nonempty_row_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_dif_max_row_length_positive(self):
        n = dif_max_row_length(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_dif_string_row_count_int(self):
        n = dif_string_row_count(_NUMERIC)
        assert isinstance(n, int)


class TestDifQueryOps:
    """Filter and sort operations."""

    def test_filter_rows_by_value_returns_list(self):
        doc = parse_dif(_NUMERIC)
        result = filter_rows_by_value(doc, 0, 1.0)
        assert isinstance(result, list)

    def test_sort_rows_by_column_returns_doc(self):
        result = sort_rows_by_column(_NUMERIC, 0)
        assert result is not None


class TestDifMutation:
    """Mutation: set_cell_value (file,dest,row,col,val), add_row, delete_row, write_dif."""

    def test_set_cell_value_produces_file(self):
        fd, dest = tempfile.mkstemp(suffix=".dif")
        os.close(fd)
        try:
            result = set_cell_value(_NUMERIC, dest, 0, 0, 99.0)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(dest)

    def test_add_row_returns_dict(self):
        doc = parse_dif_strict(_NUMERIC)
        result = add_row(doc, [7.0, 8.0, 9.0])
        assert isinstance(result, dict)

    def test_delete_row_returns_dict(self):
        doc = parse_dif_strict(_NUMERIC)
        result = delete_row(doc, 0)
        assert isinstance(result, dict)

    def test_write_dif_produces_file(self):
        doc = parse_dif_strict(_NUMERIC)
        fd, path = tempfile.mkstemp(suffix=".dif")
        os.close(fd)
        try:
            write_dif(doc, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
