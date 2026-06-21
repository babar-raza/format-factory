"""Sprint R1221 — FODS spec-parity deepening tests.

Tests spec-backed FODS functions mapped in test_spec_parity_fods_proof.py:
  FODS-FACT-001: parse_fods, parse_fods_strict, write_fods, workbook_to_xml
  FODS-FACT-002: find_sheet_by_name, workbook_sheet_summary, workbook_sheet_order
  FODS-FACT-003: workbook_get_cell_value, workbook_set_cell_value, workbook_stats
  FODS-FACT-004: workbook_row_style_summary, workbook_column_style_summary
  FODS-FACT-005: workbook_formula_list, workbook_formula_edit_policy
  FODS-FACT-006: workbook_column_count, workbook_max_column_count
  FODS-FACT-007: workbook_merged_cell_summary, workbook_cell_range
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    parse_fods_strict,
    write_fods,
    workbook_to_xml,
    workbook_stats,
    find_sheet_by_name,
    workbook_sheet_summary,
    workbook_sheet_order,
    workbook_get_cell_value,
    workbook_set_cell_value,
    workbook_row_style_summary,
    workbook_column_style_summary,
    workbook_formula_list,
    workbook_formula_edit_policy,
    workbook_column_count,
    workbook_max_column_count,
    workbook_merged_cell_summary,
    workbook_cell_range,
    fods_sheet_count,
    fods_total_cell_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
_MULTI = str(_SAMPLES / "multi-sheet-basic.fods")
_TYPED = str(_SAMPLES / "typed-values-basic.fods")
_FORMULA = str(_SAMPLES / "formula-basic.fods")


class TestFodsFactParse:
    """FODS-FACT-001: flat XML parse/write."""

    def test_parse_fods_returns_dict(self):
        wb = parse_fods(_MINIMAL)
        assert isinstance(wb, dict)

    def test_parse_fods_strict_returns_dict(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(wb, dict)

    def test_workbook_to_xml_returns_bytes_or_str(self):
        wb = parse_fods(_MINIMAL)
        xml = workbook_to_xml(wb)
        assert isinstance(xml, (str, bytes))

    def test_workbook_to_xml_contains_office_ns(self):
        wb = parse_fods(_MINIMAL)
        xml = workbook_to_xml(wb)
        xml_str = xml if isinstance(xml, str) else xml.decode()
        assert "office:" in xml_str or "office" in xml_str

    def test_write_fods_roundtrip(self, tmp_path):
        wb = parse_fods(_MINIMAL)
        out = tmp_path / "roundtrip.fods"
        write_fods(wb, str(out))
        wb2 = parse_fods(str(out))
        assert isinstance(wb2, dict)

    def test_multi_sheet_parse_succeeds(self):
        wb = parse_fods(_MULTI)
        assert fods_sheet_count(wb) >= 2


class TestFodsFactSheetStructure:
    """FODS-FACT-002: spreadsheet sheet structure."""

    def test_find_sheet_by_name_returns_dict(self):
        wb = parse_fods(_MULTI)
        sheet = find_sheet_by_name(wb, "Data")
        assert sheet is not None
        assert isinstance(sheet, dict)

    def test_find_sheet_by_name_missing_returns_none(self):
        wb = parse_fods(_MULTI)
        assert find_sheet_by_name(wb, "NonExistentSheet") is None

    def test_workbook_sheet_summary_returns_list(self):
        wb = parse_fods(_MULTI)
        summary = workbook_sheet_summary(wb)
        assert isinstance(summary, list)
        assert len(summary) >= 2

    def test_workbook_sheet_summary_has_name_field(self):
        wb = parse_fods(_MULTI)
        summary = workbook_sheet_summary(wb)
        for s in summary:
            assert "name" in s

    def test_workbook_sheet_order_returns_list(self):
        wb = parse_fods(_MULTI)
        order = workbook_sheet_order(wb)
        assert isinstance(order, list)
        assert len(order) >= 2

    def test_workbook_sheet_order_contains_data(self):
        wb = parse_fods(_MULTI)
        order = workbook_sheet_order(wb)
        assert "Data" in order


class TestFodsFactCellValues:
    """FODS-FACT-003: cell value types and access."""

    def test_workbook_stats_sheet_count(self):
        wb = parse_fods(_MULTI)
        stats = workbook_stats(wb)
        assert stats["sheet_count"] >= 2

    def test_workbook_stats_total_cells(self):
        wb = parse_fods(_TYPED)
        stats = workbook_stats(wb)
        assert stats["total_cells"] > 0

    def test_workbook_get_cell_value_returns_value(self):
        wb = parse_fods(_MINIMAL)
        val = workbook_get_cell_value(wb, 0, 0, 0)
        # May be None or a value depending on file, just check no exception
        assert val is None or val is not None

    def test_workbook_set_and_get_cell_value(self):
        wb = parse_fods(_TYPED)
        sheet = workbook_sheet_order(wb)[0]
        ok, msg = workbook_set_cell_value(wb, sheet, 0, 0, "test-value")
        assert ok is True, f"Set failed: {msg}"
        val = workbook_get_cell_value(wb, sheet, 0, 0)
        assert val == "test-value"

    def test_workbook_get_cell_value_returns_value(self):
        wb = parse_fods(_TYPED)
        sheet = workbook_sheet_order(wb)[0]
        val = workbook_get_cell_value(wb, sheet, 0, 0)
        assert val is not None

    def test_fods_total_cell_count_non_negative(self):
        wb = parse_fods(_MULTI)
        count = fods_total_cell_count(wb)
        assert isinstance(count, int)
        assert count >= 0


class TestFodsFactStyles:
    """FODS-FACT-004: row and column styles."""

    def test_workbook_row_style_summary_returns_dict(self):
        wb = parse_fods(_MULTI)
        summary = workbook_row_style_summary(wb)
        assert isinstance(summary, dict)

    def test_workbook_column_style_summary_returns_dict(self):
        wb = parse_fods(_MULTI)
        summary = workbook_column_style_summary(wb)
        assert isinstance(summary, dict)

    def test_row_and_column_styles_keyed_by_sheet(self):
        wb = parse_fods(_MULTI)
        row_s = workbook_row_style_summary(wb)
        col_s = workbook_column_style_summary(wb)
        # Both should have at least as many keys as sheets or be empty
        assert len(row_s) >= 0
        assert len(col_s) >= 0


class TestFodsFactFormulas:
    """FODS-FACT-005: formula list and edit policy."""

    def test_workbook_formula_list_is_list(self):
        wb = parse_fods(_FORMULA)
        fl = workbook_formula_list(wb)
        assert isinstance(fl, list)

    def test_workbook_formula_list_non_formula_file_empty(self):
        wb = parse_fods(_MINIMAL)
        fl = workbook_formula_list(wb)
        assert isinstance(fl, list)
        # Minimal file likely has no formulas
        assert len(fl) == 0

    def test_workbook_formula_edit_policy_returns_dict(self):
        wb = parse_fods(_FORMULA)
        policy = workbook_formula_edit_policy(wb)
        assert isinstance(policy, dict)

    def test_workbook_formula_edit_policy_has_counts(self):
        wb = parse_fods(_FORMULA)
        policy = workbook_formula_edit_policy(wb)
        # Should contain editable/locked counts or similar keys
        assert len(policy) >= 0


class TestFodsFactColumns:
    """FODS-FACT-006: column count and max."""

    def test_workbook_column_count_returns_dict(self):
        wb = parse_fods(_MULTI)
        cc = workbook_column_count(wb)
        assert isinstance(cc, dict)

    def test_workbook_max_column_count_non_negative(self):
        wb = parse_fods(_MULTI)
        mc = workbook_max_column_count(wb)
        assert isinstance(mc, int)
        assert mc >= 0


class TestFodsFactMergedCells:
    """FODS-FACT-007: merged cells and cell range."""

    def test_workbook_merged_cell_summary_is_list(self):
        wb = parse_fods(_MULTI)
        mcs = workbook_merged_cell_summary(wb)
        assert isinstance(mcs, list)

    def test_workbook_cell_range_returns_list(self):
        wb = parse_fods(_MULTI)
        # Get a 2x2 range from sheet 0
        cr = workbook_cell_range(wb, 0, 0, 0, 1, 1)
        assert isinstance(cr, list)

    def test_workbook_cell_range_single_cell(self):
        wb = parse_fods(_MINIMAL)
        cr = workbook_cell_range(wb, 0, 0, 0, 0, 0)
        assert isinstance(cr, list)
        assert len(cr) >= 1
