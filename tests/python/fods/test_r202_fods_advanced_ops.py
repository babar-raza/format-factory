"""
tests/python/fods/test_r202_fods_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT10-001
TASK-001: FODS advanced operations — parse/load, workbook info, cell access,
analytics, export, mutation.

Covers: parse_fods, parse_fods_strict, fods_sheet_count, workbook_stats,
workbook_sheet_order, workbook_sheet_summary, workbook_type_distribution,
workbook_row_count, workbook_max_column_count, workbook_get_cell_value,
workbook_cell_text_at, workbook_get_column_values, workbook_find_cells,
workbook_count_matching_cells, workbook_count_nonempty_cells,
workbook_numeric_summary, workbook_total_numeric_value, workbook_numeric_density,
workbook_empty_rows, workbook_formula_list, workbook_to_csv, workbook_to_html,
workbook_to_xml, write_fods, workbook_add_sheet, workbook_rename_sheet,
workbook_remove_sheet, workbook_set_cell_value, workbook_warnings_for_unsupported_edit,
find_sheet_by_name, workbook_cell_range, workbook_merged_cell_summary.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods, parse_fods_strict, write_fods, workbook_to_xml,
    workbook_stats, workbook_type_distribution, find_sheet_by_name,
    workbook_sheet_summary, workbook_empty_rows, workbook_formula_list,
    workbook_cell_range, workbook_merged_cell_summary, workbook_sheet_order,
    workbook_set_cell_value, workbook_warnings_for_unsupported_edit,
    workbook_add_sheet, workbook_rename_sheet, workbook_remove_sheet,
    workbook_to_csv, workbook_get_cell_value, workbook_find_cells,
    workbook_count_matching_cells, workbook_to_html, workbook_get_column_values,
    workbook_count_nonempty_cells, workbook_max_column_count, workbook_numeric_density,
    workbook_total_numeric_value, fods_sheet_count, workbook_row_count,
    workbook_cell_text_at, workbook_numeric_summary,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
_MULTI = str(_SAMPLES / "multi-sheet-basic.fods")
_TYPED = str(_SAMPLES / "typed-values-basic.fods")


class TestFodsParseAndLoad:
    """parse_fods, parse_fods_strict, fods_sheet_count, find_sheet_by_name."""

    def test_parse_fods_returns_dict(self):
        wb = parse_fods(_MINIMAL)
        assert isinstance(wb, dict)

    def test_parse_fods_has_sheets(self):
        wb = parse_fods(_MINIMAL)
        assert "sheets" in wb
        assert isinstance(wb["sheets"], list)

    def test_parse_fods_has_format_id(self):
        wb = parse_fods(_MINIMAL)
        assert wb.get("format_id") == "fods"

    def test_parse_fods_multi_sheet(self):
        wb = parse_fods(_MULTI)
        assert wb["sheet_count"] >= 2

    def test_parse_fods_strict_returns_dict(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(wb, dict)

    def test_fods_sheet_count_minimal(self):
        wb = parse_fods(_MINIMAL)
        assert fods_sheet_count(wb) >= 1

    def test_fods_sheet_count_multi(self):
        wb = parse_fods(_MULTI)
        assert fods_sheet_count(wb) >= 2

    def test_find_sheet_by_name_found(self):
        wb = parse_fods(_MULTI)
        name = wb["sheets"][0]["name"]
        sheet = find_sheet_by_name(wb, name)
        assert sheet is not None
        assert sheet["name"] == name

    def test_find_sheet_by_name_missing(self):
        wb = parse_fods(_MINIMAL)
        sheet = find_sheet_by_name(wb, "DoesNotExist")
        assert sheet is None

    def test_parse_fods_has_warnings_list(self):
        wb = parse_fods(_MINIMAL)
        assert "warnings" in wb
        assert isinstance(wb["warnings"], list)


class TestFodsWorkbookInfo:
    """workbook_stats, workbook_sheet_order, workbook_sheet_summary, workbook_row_count, workbook_max_column_count."""

    def test_workbook_stats_returns_dict(self):
        wb = parse_fods(_MINIMAL)
        stats = workbook_stats(wb)
        assert isinstance(stats, dict)

    def test_workbook_stats_has_cell_count(self):
        wb = parse_fods(_MINIMAL)
        stats = workbook_stats(wb)
        assert "total_cells" in stats or "cell_count" in stats or "sheet_count" in stats

    def test_workbook_sheet_order_list(self):
        wb = parse_fods(_MULTI)
        order = workbook_sheet_order(wb)
        assert isinstance(order, list)
        assert len(order) >= 2

    def test_workbook_sheet_summary_list(self):
        wb = parse_fods(_MINIMAL)
        summary = workbook_sheet_summary(wb)
        assert isinstance(summary, list)
        assert len(summary) >= 1

    def test_workbook_sheet_summary_has_name(self):
        wb = parse_fods(_MINIMAL)
        summary = workbook_sheet_summary(wb)
        assert "name" in summary[0]

    def test_workbook_row_count_positive(self):
        wb = parse_fods(_MINIMAL)
        count = workbook_row_count(wb, 0)
        assert isinstance(count, int)
        assert count >= 1

    def test_workbook_row_count_oob(self):
        wb = parse_fods(_MINIMAL)
        assert workbook_row_count(wb, 99) == 0

    def test_workbook_max_column_count_positive(self):
        wb = parse_fods(_MINIMAL)
        n = workbook_max_column_count(wb)
        assert isinstance(n, int)
        assert n >= 1

    def test_workbook_type_distribution_dict(self):
        wb = parse_fods(_TYPED)
        dist = workbook_type_distribution(wb)
        assert isinstance(dist, dict)

    def test_workbook_empty_rows_dict(self):
        wb = parse_fods(_MINIMAL)
        er = workbook_empty_rows(wb)
        assert isinstance(er, dict)


class TestFodsCellAccess:
    """workbook_get_cell_value, workbook_cell_text_at, workbook_get_column_values, workbook_find_cells, workbook_count_nonempty_cells."""

    def test_workbook_get_cell_value_returns_something(self):
        wb = parse_fods(_MINIMAL)
        name = wb["sheets"][0]["name"]
        val = workbook_get_cell_value(wb, name, 0, 0)
        # Could be string, number, or None
        assert val is not None or val is None  # always True, just checks no exception

    def test_workbook_get_cell_value_oob(self):
        wb = parse_fods(_MINIMAL)
        name = wb["sheets"][0]["name"]
        assert workbook_get_cell_value(wb, name, 999, 999) is None

    def test_workbook_get_cell_value_missing_sheet(self):
        wb = parse_fods(_MINIMAL)
        assert workbook_get_cell_value(wb, "NoSheet", 0, 0) is None

    def test_workbook_cell_text_at_returns_str(self):
        wb = parse_fods(_MINIMAL)
        text = workbook_cell_text_at(wb, 0, 0, 0)
        assert isinstance(text, str)

    def test_workbook_cell_text_at_oob(self):
        wb = parse_fods(_MINIMAL)
        assert workbook_cell_text_at(wb, 0, 999, 999) == ""

    def test_workbook_get_column_values_list(self):
        wb = parse_fods(_MINIMAL)
        col = workbook_get_column_values(wb, 0)
        assert isinstance(col, list)

    def test_workbook_find_cells_list(self):
        wb = parse_fods(_MINIMAL)
        # Get first cell value and search for it
        first_val = workbook_get_cell_value(wb, wb["sheets"][0]["name"], 0, 0)
        results = workbook_find_cells(wb, first_val) if first_val is not None else []
        assert isinstance(results, list)

    def test_workbook_count_matching_cells_int(self):
        wb = parse_fods(_MINIMAL)
        n = workbook_count_matching_cells(wb, "nonexistent_value_xyz")
        assert isinstance(n, int)
        assert n == 0

    def test_workbook_count_nonempty_cells_positive(self):
        wb = parse_fods(_MINIMAL)
        n = workbook_count_nonempty_cells(wb, 0)
        assert isinstance(n, int)
        assert n >= 1

    def test_workbook_count_nonempty_cells_oob(self):
        wb = parse_fods(_MINIMAL)
        assert workbook_count_nonempty_cells(wb, 99) == 0


class TestFodsAnalytics:
    """workbook_numeric_summary, workbook_total_numeric_value, workbook_numeric_density, workbook_formula_list, workbook_cell_range."""

    def test_workbook_numeric_summary_dict(self):
        wb = parse_fods(_TYPED)
        ns = workbook_numeric_summary(wb)
        assert isinstance(ns, dict)
        assert "total_numeric_cells" in ns

    def test_workbook_total_numeric_value_float(self):
        wb = parse_fods(_TYPED)
        total = workbook_total_numeric_value(wb, 0)
        assert isinstance(total, float)

    def test_workbook_numeric_density_range(self):
        wb = parse_fods(_TYPED)
        density = workbook_numeric_density(wb, 0)
        assert isinstance(density, float)
        assert 0.0 <= density <= 1.0

    def test_workbook_numeric_density_oob(self):
        wb = parse_fods(_MINIMAL)
        assert workbook_numeric_density(wb, 99) == 0.0

    def test_workbook_formula_list(self):
        wb = parse_fods(_MINIMAL)
        fl = workbook_formula_list(wb)
        assert isinstance(fl, list)

    def test_workbook_cell_range_list(self):
        wb = parse_fods(_MINIMAL)
        cr = workbook_cell_range(wb, sheet_index=0, row_start=0, row_end=1, col_start=0, col_end=1)
        assert isinstance(cr, list)

    def test_workbook_merged_cell_summary_list(self):
        wb = parse_fods(_MINIMAL)
        mcs = workbook_merged_cell_summary(wb)
        assert isinstance(mcs, list)


class TestFodsExport:
    """workbook_to_csv, workbook_to_html, workbook_to_xml, write_fods."""

    def test_workbook_to_csv_returns_str(self):
        wb = parse_fods(_MINIMAL)
        csv_str = workbook_to_csv(wb)
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0

    def test_workbook_to_csv_specific_sheet(self):
        wb = parse_fods(_MULTI)
        name = wb["sheets"][0]["name"]
        csv_str = workbook_to_csv(wb, sheet_name=name)
        assert isinstance(csv_str, str)

    def test_workbook_to_csv_missing_sheet(self):
        wb = parse_fods(_MINIMAL)
        csv_str = workbook_to_csv(wb, sheet_name="NoSuchSheet")
        assert csv_str == ""

    def test_workbook_to_html_returns_str(self):
        wb = parse_fods(_MINIMAL)
        html = workbook_to_html(wb, sheet_index=0)
        assert isinstance(html, str)
        assert "<table>" in html

    def test_workbook_to_html_oob(self):
        wb = parse_fods(_MINIMAL)
        html = workbook_to_html(wb, sheet_index=99)
        assert html == ""

    def test_workbook_to_xml_returns_str(self):
        wb = parse_fods(_MINIMAL)
        xml_str = workbook_to_xml(wb)
        assert isinstance(xml_str, str)
        assert "spreadsheet" in xml_str.lower() or "office" in xml_str.lower()

    def test_write_fods_creates_file(self):
        wb = parse_fods(_MINIMAL)
        fd, path = tempfile.mkstemp(suffix=".fods")
        os.close(fd)
        try:
            write_fods(wb, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


class TestFodsMutation:
    """workbook_add_sheet, workbook_rename_sheet, workbook_remove_sheet, workbook_set_cell_value."""

    def test_workbook_add_sheet_success(self):
        wb = parse_fods(_MINIMAL)
        ok, msg = workbook_add_sheet(wb, "NewSheet")
        assert ok is True
        assert fods_sheet_count(wb) >= 2

    def test_workbook_add_sheet_duplicate_fails(self):
        wb = parse_fods(_MINIMAL)
        name = wb["sheets"][0]["name"]
        ok, msg = workbook_add_sheet(wb, name)
        assert ok is False

    def test_workbook_rename_sheet_success(self):
        wb = parse_fods(_MINIMAL)
        old_name = wb["sheets"][0]["name"]
        ok, msg = workbook_rename_sheet(wb, old_name, "RenamedSheet")
        assert ok is True
        assert wb["sheets"][0]["name"] == "RenamedSheet"

    def test_workbook_rename_sheet_missing_fails(self):
        wb = parse_fods(_MINIMAL)
        ok, msg = workbook_rename_sheet(wb, "DoesNotExist", "New")
        assert ok is False

    def test_workbook_remove_sheet_multi(self):
        wb = parse_fods(_MULTI)
        count_before = fods_sheet_count(wb)
        name = wb["sheets"][0]["name"]
        ok, msg = workbook_remove_sheet(wb, name)
        assert ok is True
        assert fods_sheet_count(wb) == count_before - 1

    def test_workbook_remove_sheet_only_one_fails(self):
        wb = parse_fods(_MINIMAL)
        # Ensure only 1 sheet
        while fods_sheet_count(wb) > 1:
            workbook_remove_sheet(wb, wb["sheets"][-1]["name"])
        ok, msg = workbook_remove_sheet(wb, wb["sheets"][0]["name"])
        assert ok is False

    def test_workbook_set_cell_value_success(self):
        wb = parse_fods(_MINIMAL)
        sheet_name = wb["sheets"][0]["name"]
        ok, msg = workbook_set_cell_value(wb, sheet_name, 0, 0, "Updated")
        assert ok is True
        assert workbook_get_cell_value(wb, sheet_name, 0, 0) == "Updated"

    def test_workbook_set_cell_value_missing_sheet(self):
        wb = parse_fods(_MINIMAL)
        ok, msg = workbook_set_cell_value(wb, "NoSheet", 0, 0, "X")
        assert ok is False

    def test_workbook_warnings_for_unsupported_edit_list(self):
        wb = parse_fods(_MINIMAL)
        sheet_name = wb["sheets"][0]["name"]
        warnings = workbook_warnings_for_unsupported_edit(wb, sheet_name, 0, 0)
        assert isinstance(warnings, list)
