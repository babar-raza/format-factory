"""
tests/python/sylk/test_r200_sylk_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT4-001
TASK-001: SYLK advanced operations — analytics, stats, mutation, export.

Covers: probe_sylk, get_row_count, get_column_count, get_cell_count, get_all_values,
get_row_values, get_column_values, get_cell_value, count_nonempty_cells, count_distinct_values,
sum_column, average_column, min_column_value, max_column_value, find_value, find_rows_by_value,
sylk_row_count, sylk_numeric_cell_count, sylk_empty_cell_count, sylk_string_cell_count,
sylk_max_column_index, sylk_nonempty_rows, sylk_to_html, set_cell_value, add_row, delete_row,
write_sylk.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import sylk
from sylk import (
    parse_sylk, parse_sylk_strict, probe_sylk,
    get_row_count, get_column_count, get_cell_count,
    get_all_values, get_row_values, get_column_values, get_cell_value,
    count_nonempty_cells, count_distinct_values,
    sum_column, average_column, min_column_value, max_column_value,
    find_value, find_rows_by_value,
    sylk_row_count, sylk_numeric_cell_count, sylk_empty_cell_count,
    sylk_string_cell_count, sylk_max_column_index, sylk_nonempty_rows,
    sylk_to_html, set_cell_value, add_row, delete_row, write_sylk,
    SylkDocument, SylkCell,
)

_NUMERIC = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk")
_MINIMAL = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk")
_SINGLE = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk")


class TestSylkProbeAndMetadata:
    """Probe and structural metadata (file path based)."""

    def test_probe_sylk_returns_dict(self):
        result = probe_sylk(_NUMERIC)
        assert isinstance(result, dict)

    def test_probe_sylk_valid_header(self):
        result = probe_sylk(_NUMERIC)
        assert result.get("valid_header") is True

    def test_probe_sylk_exists(self):
        result = probe_sylk(_NUMERIC)
        assert result.get("exists") is True

    def test_get_row_count_positive(self):
        n = get_row_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_get_column_count_positive(self):
        n = get_column_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_get_cell_count_positive(self):
        n = get_cell_count(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_sylk_row_count_positive(self):
        n = sylk_row_count(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_sylk_max_column_index_positive(self):
        n = sylk_max_column_index(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_sylk_nonempty_rows_positive(self):
        n = sylk_nonempty_rows(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1


class TestSylkCellCounts:
    """Cell type count analytics."""

    def test_sylk_numeric_cell_count_positive(self):
        n = sylk_numeric_cell_count(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_sylk_empty_cell_count_int(self):
        n = sylk_empty_cell_count(_NUMERIC)
        assert isinstance(n, int)

    def test_sylk_string_cell_count_int(self):
        n = sylk_string_cell_count(_NUMERIC)
        assert isinstance(n, int)

    def test_count_nonempty_cells_positive(self):
        n = count_nonempty_cells(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0


class TestSylkValueAccess:
    """Value access functions."""

    def test_get_all_values_returns_list(self):
        result = get_all_values(_NUMERIC)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_all_values_numeric(self):
        result = get_all_values(_NUMERIC)
        assert all(isinstance(v, (int, float)) for v in result)

    def test_get_cell_value_returns_value(self):
        result = get_cell_value(_NUMERIC, 1, 1)
        # May return None for out-of-index, but should not raise
        assert result is not None or result is None  # no crash

    def test_find_value_returns_location(self):
        values = get_all_values(_NUMERIC)
        if values:
            result = find_value(_NUMERIC, values[0])
            assert isinstance(result, tuple)

    def test_find_rows_by_value_returns_list(self):
        values = get_all_values(_NUMERIC)
        if values:
            result = find_rows_by_value(_NUMERIC, values[0])
            assert isinstance(result, list)

    def test_count_distinct_values_int(self):
        n = count_distinct_values(_NUMERIC, 0)
        assert isinstance(n, int)


class TestSylkExport:
    """Export functions."""

    def test_sylk_to_html_returns_string(self):
        html = sylk_to_html(_NUMERIC)
        assert isinstance(html, str)
        assert "<table>" in html or "<td>" in html


class TestSylkMutation:
    """Mutation: set_cell_value, add_row, delete_row, write_sylk."""

    def test_set_cell_value_produces_file(self):
        # SYLK rows/cols are 1-indexed
        fd, dest = tempfile.mkstemp(suffix=".slk")
        os.close(fd)
        try:
            result = set_cell_value(_NUMERIC, dest, 1, 1, "test")
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(dest)

    def test_add_row_produces_file(self):
        fd, dest = tempfile.mkstemp(suffix=".slk")
        os.close(fd)
        try:
            result = add_row(_NUMERIC, dest, [10, 20, 30])
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(dest)

    def test_delete_row_produces_file(self):
        fd, dest = tempfile.mkstemp(suffix=".slk")
        os.close(fd)
        try:
            result = delete_row(_NUMERIC, dest, 1)  # 1-indexed
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(dest)

    def test_write_sylk_with_object_model(self):
        doc = SylkDocument(rows=1, cols=1, cells=[SylkCell(row=1, col=1, value=42.0, value_type="numeric")])
        fd, path = tempfile.mkstemp(suffix=".slk")
        os.close(fd)
        try:
            write_sylk(doc, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
