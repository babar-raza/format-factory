"""
tests/python/ods/test_r199_ods_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT2-001
TASK-009: ODS advanced operations — spreadsheet stats, analytics, cell type distribution.

Covers: probe_ods, count_sheets, spreadsheet_stats, ods_sheet_name_list, sheet_name_order,
ods_cell_type_distribution, ods_formula_cell_count, ods_data_validation_count,
ods_numeric_cell_count, ods_empty_cell_count, ods_max_row_length, ods_to_html,
sum_column, sum_row, get_all_values, count_nonempty_cells, count_distinct_values,
filter_rows_by_value, write_ods/set_cell_value/add_sheet.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ods
from ods import (
    parse_ods, probe_ods, count_sheets, spreadsheet_stats,
    ods_sheet_name_list, sheet_name_order, ods_cell_type_distribution,
    ods_formula_cell_count, ods_data_validation_count,
    ods_numeric_cell_count, ods_empty_cell_count, ods_max_row_length,
    ods_to_html, sum_column, sum_row, get_all_values, count_nonempty_cells,
    count_distinct_values, filter_rows_by_value,
    write_ods, set_cell_value, add_sheet, remove_sheet, rename_sheet,
    add_row, delete_row, OdsDocument, OdsSheet, OdsRow, OdsCell,
)

_MINIMAL = str(_REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods")
_NUMERIC = str(_REPO / "samples" / "by-format" / "ods" / "valid" / "numeric-row.ods")


class TestOdsProbeAndMetadata:
    """Probe and structural metadata functions."""

    def test_probe_ods_returns_dict(self):
        result = probe_ods(_MINIMAL)
        assert isinstance(result, dict)

    def test_probe_ods_has_expected_keys(self):
        result = probe_ods(_MINIMAL)
        assert "exists" in result
        assert result["exists"] is True
        assert "valid_container" in result
        assert result["valid_container"] is True

    def test_count_sheets_returns_int(self):
        n = count_sheets(_MINIMAL)
        assert isinstance(n, int)
        assert n >= 1

    def test_count_sheets_numeric_row(self):
        n = count_sheets(_NUMERIC)
        assert isinstance(n, int)
        assert n >= 1

    def test_ods_sheet_name_list_returns_list(self):
        wb = parse_ods(_MINIMAL)
        names = ods_sheet_name_list(wb)
        assert isinstance(names, list)
        assert len(names) >= 1

    def test_sheet_name_order_matches_name_list(self):
        wb = parse_ods(_MINIMAL)
        order = sheet_name_order(wb)
        names = ods_sheet_name_list(wb)
        assert order == names


class TestOdsSpreadsheetStats:
    """Spreadsheet-level analytics."""

    def test_spreadsheet_stats_returns_dict(self):
        wb = parse_ods(_MINIMAL)
        stats = spreadsheet_stats(wb)
        assert isinstance(stats, dict)

    def test_spreadsheet_stats_has_sheet_count(self):
        wb = parse_ods(_MINIMAL)
        stats = spreadsheet_stats(wb)
        assert "sheet_count" in stats
        assert stats["sheet_count"] >= 1

    def test_spreadsheet_stats_total_cells_positive(self):
        wb = parse_ods(_MINIMAL)
        stats = spreadsheet_stats(wb)
        assert "total_cells" in stats
        assert stats["total_cells"] >= 0

    def test_spreadsheet_stats_has_per_sheet(self):
        wb = parse_ods(_MINIMAL)
        stats = spreadsheet_stats(wb)
        assert "per_sheet" in stats
        assert isinstance(stats["per_sheet"], list)


class TestOdsCellTypeDistribution:
    """Cell type distribution and formula/validation counts."""

    def test_cell_type_distribution_returns_dict(self):
        wb = parse_ods(_NUMERIC)
        result = ods_cell_type_distribution(wb)
        assert isinstance(result, dict)

    def test_cell_type_distribution_has_by_type(self):
        wb = parse_ods(_NUMERIC)
        result = ods_cell_type_distribution(wb)
        assert "by_type" in result
        assert isinstance(result["by_type"], dict)

    def test_cell_type_distribution_numeric_detected(self):
        wb = parse_ods(_NUMERIC)
        result = ods_cell_type_distribution(wb)
        assert result["by_type"].get("numeric", 0) > 0

    def test_formula_cell_count_zero_for_simple(self):
        wb = parse_ods(_NUMERIC)
        count = ods_formula_cell_count(wb)
        assert isinstance(count, int)
        assert count == 0

    def test_data_validation_count_zero_for_simple(self):
        wb = parse_ods(_NUMERIC)
        count = ods_data_validation_count(wb)
        assert isinstance(count, int)
        assert count == 0


class TestOdsPathAnalytics:
    """Analytics functions that take file path."""

    def test_ods_numeric_cell_count_positive(self):
        n = ods_numeric_cell_count(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_ods_empty_cell_count_int(self):
        n = ods_empty_cell_count(_NUMERIC)
        assert isinstance(n, int)

    def test_ods_max_row_length_positive(self):
        n = ods_max_row_length(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_get_all_values_list(self):
        vals = get_all_values(_NUMERIC)
        assert isinstance(vals, list)
        assert len(vals) > 0

    def test_count_nonempty_cells_positive(self):
        n = count_nonempty_cells(_NUMERIC)
        assert isinstance(n, int)
        assert n > 0

    def test_count_distinct_values_positive(self):
        n = count_distinct_values(_NUMERIC, 0)
        assert isinstance(n, int)
        assert n >= 1

    def test_sum_column_numeric(self):
        result = sum_column(_NUMERIC, 0, 0)
        assert isinstance(result, (int, float))

    def test_sum_row_numeric(self):
        result = sum_row(_NUMERIC, 0, 0)
        assert isinstance(result, (int, float))
        assert result > 0

    def test_filter_rows_by_value_returns_list(self):
        result = filter_rows_by_value(_NUMERIC, 0, 0, 1.0)
        assert isinstance(result, list)

    def test_ods_to_html_returns_string(self):
        html = ods_to_html(_NUMERIC)
        assert isinstance(html, str)
        assert "<table>" in html or "<td>" in html


class TestOdsWriteAndEdit:
    """Write, set_cell_value, add/remove sheet, add/delete row (use parse_ods_strict)."""

    def test_write_ods_produces_file(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        fd, path = tempfile.mkstemp(suffix=".ods")
        os.close(fd)
        try:
            write_ods(doc, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_set_cell_value_returns_tuple(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        result = set_cell_value(doc, 0, 0, 0, "changed")
        assert isinstance(result, tuple)
        assert result[0] is True

    def test_add_sheet_returns_tuple(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        result = add_sheet(doc, "NewSheet")
        assert isinstance(result, tuple)

    def test_remove_sheet_returns_tuple(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        add_sheet(doc, "ToRemove")
        result = remove_sheet(doc, "ToRemove")
        assert result is not None

    def test_rename_sheet_returns_result(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        result = rename_sheet(doc, doc.sheets[0].name, "RenamedSheet")
        assert result is not None

    def test_add_row_returns_result(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        result = add_row(doc, 0, [1.0, 2.0, 3.0])
        assert result is not None

    def test_delete_row_returns_result(self):
        from ods import parse_ods_strict
        doc = parse_ods_strict(_MINIMAL)
        result = delete_row(doc, 0, 0)
        assert result is not None
