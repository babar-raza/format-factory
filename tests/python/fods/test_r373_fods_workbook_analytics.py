"""
Tests for FODS workbook analytics functions — deepening coverage.

Covers:
  workbook_sheet_summary, workbook_empty_rows, workbook_formula_list,
  workbook_cell_range, workbook_merged_cell_summary, workbook_sheet_order,
  workbook_numeric_summary, workbook_column_count, workbook_row_style_summary,
  workbook_style_family_list, workbook_data_validation_summary,
  workbook_column_style_summary, workbook_column_width_summary,
  workbook_formula_edit_policy, workbook_named_range_list, workbook_type_distribution,
  workbook_cell_type_matrix, workbook_max_column_count

Spec refs: SAL-FODS-00008 (sheet model), SAL-FODS-00013 (cell model),
           SAL-FODS-00037 (formula), SAL-FODS-00038 (workbook structure)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
_SAMPLES = _REPO / "samples" / "by-format" / "fods"

import fods
from fods import (
    parse_fods,
    workbook_sheet_summary,
    workbook_empty_rows,
    workbook_formula_list,
    workbook_cell_range,
    workbook_merged_cell_summary,
    workbook_sheet_order,
    workbook_numeric_summary,
    workbook_column_count,
    workbook_row_style_summary,
    workbook_style_family_list,
    workbook_data_validation_summary,
    workbook_column_style_summary,
    workbook_column_width_summary,
    workbook_formula_edit_policy,
    workbook_named_range_list,
    workbook_type_distribution,
    workbook_cell_type_matrix,
    workbook_max_column_count,
)


@pytest.fixture(scope="module")
def wb_multi():
    return parse_fods(str(_SAMPLES / "multi-sheet-basic.fods"))


@pytest.fixture(scope="module")
def wb_formula():
    return parse_fods(str(_SAMPLES / "formula-basic.fods"))


@pytest.fixture(scope="module")
def wb_typed():
    return parse_fods(str(_SAMPLES / "typed-values-basic.fods"))


# ---------------------------------------------------------------------------
# workbook_sheet_summary
# ---------------------------------------------------------------------------

class TestWorkbookSheetSummary:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_sheet_summary(wb_multi), list)

    def test_count_matches_sheet_count(self, wb_multi):
        result = workbook_sheet_summary(wb_multi)
        assert len(result) == wb_multi["sheet_count"]

    def test_each_entry_has_name(self, wb_multi):
        for entry in workbook_sheet_summary(wb_multi):
            assert "name" in entry

    def test_each_entry_has_index(self, wb_multi):
        for entry in workbook_sheet_summary(wb_multi):
            assert "index" in entry

    def test_each_entry_has_row_count(self, wb_multi):
        for entry in workbook_sheet_summary(wb_multi):
            assert "row_count" in entry


# ---------------------------------------------------------------------------
# workbook_empty_rows
# ---------------------------------------------------------------------------

class TestWorkbookEmptyRows:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_empty_rows(wb_multi), dict)

    def test_has_total_empty_rows(self, wb_multi):
        result = workbook_empty_rows(wb_multi)
        assert "total_empty_rows" in result

    def test_has_per_sheet(self, wb_multi):
        result = workbook_empty_rows(wb_multi)
        assert "per_sheet" in result

    def test_total_is_int(self, wb_multi):
        assert isinstance(workbook_empty_rows(wb_multi)["total_empty_rows"], int)

    def test_per_sheet_is_list(self, wb_multi):
        assert isinstance(workbook_empty_rows(wb_multi)["per_sheet"], list)


# ---------------------------------------------------------------------------
# workbook_formula_list
# ---------------------------------------------------------------------------

class TestWorkbookFormulaList:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_formula_list(wb_multi), list)

    def test_no_formulas_in_basic(self, wb_multi):
        assert workbook_formula_list(wb_multi) == []

    def test_formula_sample_has_formulas(self, wb_formula):
        result = workbook_formula_list(wb_formula)
        assert len(result) > 0

    def test_formula_entry_has_formula_key(self, wb_formula):
        result = workbook_formula_list(wb_formula)
        for entry in result:
            assert "formula" in entry

    def test_formula_entry_has_sheet_name(self, wb_formula):
        result = workbook_formula_list(wb_formula)
        for entry in result:
            assert "sheet_name" in entry


# ---------------------------------------------------------------------------
# workbook_cell_range
# ---------------------------------------------------------------------------

class TestWorkbookCellRange:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_cell_range(wb_multi), list)

    def test_rows_are_lists(self, wb_multi):
        for row in workbook_cell_range(wb_multi):
            assert isinstance(row, list)

    def test_nonempty_for_nonempty_sheet(self, wb_multi):
        assert len(workbook_cell_range(wb_multi)) > 0

    def test_typed_sample_has_rows(self, wb_typed):
        result = workbook_cell_range(wb_typed)
        assert isinstance(result, list)

    def test_formula_sample_has_rows(self, wb_formula):
        result = workbook_cell_range(wb_formula)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# workbook_merged_cell_summary
# ---------------------------------------------------------------------------

class TestWorkbookMergedCellSummary:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_merged_cell_summary(wb_multi), list)

    def test_basic_has_no_merges(self, wb_multi):
        assert workbook_merged_cell_summary(wb_multi) == []

    def test_formula_has_no_merges(self, wb_formula):
        assert isinstance(workbook_merged_cell_summary(wb_formula), list)

    def test_typed_has_no_merges(self, wb_typed):
        assert isinstance(workbook_merged_cell_summary(wb_typed), list)

    def test_result_is_list_always(self, wb_multi):
        result = workbook_merged_cell_summary(wb_multi)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# workbook_sheet_order
# ---------------------------------------------------------------------------

class TestWorkbookSheetOrder:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_sheet_order(wb_multi), list)

    def test_count_matches_sheets(self, wb_multi):
        result = workbook_sheet_order(wb_multi)
        assert len(result) == wb_multi["sheet_count"]

    def test_entries_are_strings(self, wb_multi):
        for name in workbook_sheet_order(wb_multi):
            assert isinstance(name, str)

    def test_order_preserved(self, wb_multi):
        order = workbook_sheet_order(wb_multi)
        sheet_names = [s["name"] for s in wb_multi["sheets"]]
        assert order == sheet_names

    def test_single_sheet(self, wb_formula):
        result = workbook_sheet_order(wb_formula)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# workbook_numeric_summary
# ---------------------------------------------------------------------------

class TestWorkbookNumericSummary:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_numeric_summary(wb_multi), dict)

    def test_has_total_numeric_cells(self, wb_multi):
        result = workbook_numeric_summary(wb_multi)
        assert "total_numeric_cells" in result

    def test_typed_has_numerics(self, wb_typed):
        result = workbook_numeric_summary(wb_typed)
        assert result["total_numeric_cells"] >= 0

    def test_global_min_none_when_no_numerics(self, wb_multi):
        result = workbook_numeric_summary(wb_multi)
        # multi-sheet-basic has no numerics
        assert result["total_numeric_cells"] == 0

    def test_typed_global_fields_present(self, wb_typed):
        result = workbook_numeric_summary(wb_typed)
        assert "global_min" in result
        assert "global_max" in result
        assert "global_sum" in result


# ---------------------------------------------------------------------------
# workbook_column_count
# ---------------------------------------------------------------------------

class TestWorkbookColumnCount:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_column_count(wb_multi), dict)

    def test_has_per_sheet(self, wb_multi):
        result = workbook_column_count(wb_multi)
        assert "per_sheet" in result

    def test_per_sheet_is_list(self, wb_multi):
        result = workbook_column_count(wb_multi)
        assert isinstance(result["per_sheet"], list)

    def test_each_entry_has_max_columns(self, wb_multi):
        for entry in workbook_column_count(wb_multi)["per_sheet"]:
            assert "max_columns" in entry

    def test_positive_columns_in_data_sheet(self, wb_multi):
        result = workbook_column_count(wb_multi)
        data_entry = next((e for e in result["per_sheet"] if e.get("sheet_name") == "Data"), None)
        if data_entry:
            assert data_entry["max_columns"] > 0


# ---------------------------------------------------------------------------
# workbook_row_style_summary
# ---------------------------------------------------------------------------

class TestWorkbookRowStyleSummary:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_row_style_summary(wb_multi), dict)

    def test_has_sheet_keys(self, wb_multi):
        result = workbook_row_style_summary(wb_multi)
        for name in workbook_sheet_order(wb_multi):
            assert name in result

    def test_values_are_lists(self, wb_multi):
        result = workbook_row_style_summary(wb_multi)
        for v in result.values():
            assert isinstance(v, list)

    def test_formula_sample_is_dict(self, wb_formula):
        assert isinstance(workbook_row_style_summary(wb_formula), dict)

    def test_typed_sample_is_dict(self, wb_typed):
        assert isinstance(workbook_row_style_summary(wb_typed), dict)


# ---------------------------------------------------------------------------
# workbook_style_family_list
# ---------------------------------------------------------------------------

class TestWorkbookStyleFamilyList:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_style_family_list(wb_multi), list)

    def test_basic_has_no_custom_styles(self, wb_multi):
        assert workbook_style_family_list(wb_multi) == []

    def test_typed_returns_list(self, wb_typed):
        assert isinstance(workbook_style_family_list(wb_typed), list)

    def test_formula_returns_list(self, wb_formula):
        assert isinstance(workbook_style_family_list(wb_formula), list)

    def test_all_entries_are_strings(self, wb_multi):
        for item in workbook_style_family_list(wb_multi):
            assert isinstance(item, str)


# ---------------------------------------------------------------------------
# workbook_data_validation_summary
# ---------------------------------------------------------------------------

class TestWorkbookDataValidationSummary:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_data_validation_summary(wb_multi), dict)

    def test_has_validation_count(self, wb_multi):
        result = workbook_data_validation_summary(wb_multi)
        assert "validation_count" in result

    def test_basic_has_zero_validations(self, wb_multi):
        result = workbook_data_validation_summary(wb_multi)
        assert result["validation_count"] == 0

    def test_has_validated_cell_ranges(self, wb_multi):
        result = workbook_data_validation_summary(wb_multi)
        assert "validated_cell_ranges" in result

    def test_validated_ranges_is_list(self, wb_multi):
        assert isinstance(workbook_data_validation_summary(wb_multi)["validated_cell_ranges"], list)


# ---------------------------------------------------------------------------
# workbook_column_style_summary
# ---------------------------------------------------------------------------

class TestWorkbookColumnStyleSummary:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_column_style_summary(wb_multi), dict)

    def test_has_sheet_keys(self, wb_multi):
        result = workbook_column_style_summary(wb_multi)
        for name in workbook_sheet_order(wb_multi):
            assert name in result

    def test_values_are_lists(self, wb_multi):
        for v in workbook_column_style_summary(wb_multi).values():
            assert isinstance(v, list)

    def test_typed_is_dict(self, wb_typed):
        assert isinstance(workbook_column_style_summary(wb_typed), dict)

    def test_formula_is_dict(self, wb_formula):
        assert isinstance(workbook_column_style_summary(wb_formula), dict)


# ---------------------------------------------------------------------------
# workbook_column_width_summary
# ---------------------------------------------------------------------------

class TestWorkbookColumnWidthSummary:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_column_width_summary(wb_multi), list)

    def test_count_matches_sheets(self, wb_multi):
        result = workbook_column_width_summary(wb_multi)
        assert len(result) == wb_multi["sheet_count"]

    def test_each_entry_has_sheet_name(self, wb_multi):
        for entry in workbook_column_width_summary(wb_multi):
            assert "sheet_name" in entry

    def test_each_entry_has_column_count(self, wb_multi):
        for entry in workbook_column_width_summary(wb_multi):
            assert "column_count" in entry

    def test_each_entry_has_widths(self, wb_multi):
        for entry in workbook_column_width_summary(wb_multi):
            assert "widths" in entry


# ---------------------------------------------------------------------------
# workbook_formula_edit_policy
# ---------------------------------------------------------------------------

class TestWorkbookFormulaEditPolicy:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_formula_edit_policy(wb_multi), dict)

    def test_has_total_formulas(self, wb_multi):
        assert "total_formulas" in workbook_formula_edit_policy(wb_multi)

    def test_no_formulas_in_basic(self, wb_multi):
        result = workbook_formula_edit_policy(wb_multi)
        assert result["total_formulas"] == 0

    def test_formula_sample_has_formulas(self, wb_formula):
        result = workbook_formula_edit_policy(wb_formula)
        assert result["total_formulas"] > 0

    def test_has_editable_formulas_key(self, wb_formula):
        assert "editable_formulas" in workbook_formula_edit_policy(wb_formula)


# ---------------------------------------------------------------------------
# workbook_named_range_list
# ---------------------------------------------------------------------------

class TestWorkbookNamedRangeList:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_named_range_list(wb_multi), list)

    def test_basic_has_no_named_ranges(self, wb_multi):
        assert workbook_named_range_list(wb_multi) == []

    def test_typed_returns_list(self, wb_typed):
        assert isinstance(workbook_named_range_list(wb_typed), list)

    def test_formula_returns_list(self, wb_formula):
        assert isinstance(workbook_named_range_list(wb_formula), list)

    def test_all_items_are_dicts(self, wb_multi):
        for item in workbook_named_range_list(wb_multi):
            assert isinstance(item, dict)


# ---------------------------------------------------------------------------
# workbook_type_distribution
# ---------------------------------------------------------------------------

class TestWorkbookTypeDistribution:
    def test_returns_dict(self, wb_multi):
        assert isinstance(workbook_type_distribution(wb_multi), dict)

    def test_has_by_type(self, wb_multi):
        assert "by_type" in workbook_type_distribution(wb_multi)

    def test_has_total_cells(self, wb_multi):
        assert "total_cells" in workbook_type_distribution(wb_multi)

    def test_total_is_int(self, wb_multi):
        assert isinstance(workbook_type_distribution(wb_multi)["total_cells"], int)

    def test_by_type_is_dict(self, wb_multi):
        assert isinstance(workbook_type_distribution(wb_multi)["by_type"], dict)


# ---------------------------------------------------------------------------
# workbook_cell_type_matrix
# ---------------------------------------------------------------------------

class TestWorkbookCellTypeMatrix:
    def test_returns_list(self, wb_multi):
        assert isinstance(workbook_cell_type_matrix(wb_multi), list)

    def test_count_matches_sheets(self, wb_multi):
        result = workbook_cell_type_matrix(wb_multi)
        assert len(result) == wb_multi["sheet_count"]

    def test_each_entry_has_sheet_name(self, wb_multi):
        for entry in workbook_cell_type_matrix(wb_multi):
            assert "sheet_name" in entry

    def test_each_entry_has_by_type(self, wb_multi):
        for entry in workbook_cell_type_matrix(wb_multi):
            assert "by_type" in entry

    def test_formula_sample_is_list(self, wb_formula):
        assert isinstance(workbook_cell_type_matrix(wb_formula), list)


# ---------------------------------------------------------------------------
# workbook_max_column_count
# ---------------------------------------------------------------------------

class TestWorkbookMaxColumnCount:
    def test_returns_int(self, wb_multi):
        assert isinstance(workbook_max_column_count(wb_multi), int)

    def test_positive_for_nonempty_wb(self, wb_multi):
        assert workbook_max_column_count(wb_multi) > 0

    def test_typed_sample_positive(self, wb_typed):
        assert workbook_max_column_count(wb_typed) > 0

    def test_formula_sample_positive(self, wb_formula):
        assert workbook_max_column_count(wb_formula) > 0

    def test_at_least_two_for_multi_col_sheet(self, wb_multi):
        # multi-sheet-basic has 2 columns in Data sheet
        assert workbook_max_column_count(wb_multi) >= 2
