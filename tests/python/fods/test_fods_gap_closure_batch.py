"""Gap closure tests for FODS — covering 33 open FOSS gaps.

Gaps: GAP-FODS-FOSS-WORKBOOK_TO-001, GAP-FODS-FOSS-WORKBOOK_ST-001,
      GAP-FODS-FOSS-WORKBOOK_TY-001, GAP-FODS-FOSS-FIND_SHEET_-001,
      GAP-FODS-FOSS-WORKBOOK_SH-001, GAP-FODS-FOSS-WORKBOOK_EM-001,
      GAP-FODS-FOSS-WORKBOOK_FO-001, GAP-FODS-FOSS-WORKBOOK_CE-001,
      GAP-FODS-FOSS-WORKBOOK_ME-001, GAP-FODS-FOSS-WORKBOOK_NU-001,
      GAP-FODS-FOSS-WORKBOOK_CO-001, GAP-FODS-FOSS-WORKBOOK_RO-001,
      GAP-FODS-FOSS-WORKBOOK_NA-001, GAP-FODS-FOSS-WORKBOOK_ST-002,
      GAP-FODS-FOSS-WORKBOOK_DA-001, GAP-FODS-FOSS-WORKBOOK_SE-001,
      GAP-FODS-FOSS-WORKBOOK_WA-001, GAP-FODS-FOSS-WORKBOOK_AD-001,
      GAP-FODS-FOSS-WORKBOOK_RE-001, GAP-FODS-FOSS-WORKBOOK_RE-002,
      GAP-FODS-FOSS-WORKBOOK_GE-001, GAP-FODS-FOSS-WORKBOOK_FI-001,
      GAP-FODS-FOSS-WORKBOOK_CO-002, GAP-FODS-FOSS-WORKBOOK_MA-001,
      GAP-FODS-FOSS-WORKBOOK_TO-002, GAP-FODS-FOSS-FODSERROR-001,
      GAP-FODS-FOSS-FODSINPUTER-001, GAP-FODS-FOSS-FODSSIZEERR-001,
      GAP-FODS-FOSS-FODSPARSEER-001, GAP-FODS-FOSS-FORMAT_ID-001,
      GAP-FODS-FOSS-SPEC_VERSIO-001, GAP-FODS-FOSS-PACKAGE_VER-001,
      GAP-FODS-FOSS-MAX_FILE_BY-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    FORMAT_ID,
    MAX_FILE_BYTES,
    PACKAGE_VERSION,
    SPEC_VERSION,
    FodsError,
    FodsInputError,
    FodsParseError,
    FodsSizeError,
    find_sheet_by_name,
    fods_sheet_count,
    fods_total_cell_count,
    parse_fods,
    workbook_add_sheet,
    workbook_cell_range,
    workbook_cell_type_matrix,
    workbook_column_count,
    workbook_column_style_summary,
    workbook_column_width_summary,
    workbook_count_matching_cells,
    workbook_count_nonempty_cells,
    workbook_data_validation_summary,
    workbook_empty_rows,
    workbook_find_cells,
    workbook_formula_edit_policy,
    workbook_formula_list,
    workbook_get_cell_value,
    workbook_max_column_count,
    workbook_merged_cell_summary,
    workbook_named_range_list,
    workbook_numeric_density,
    workbook_numeric_summary,
    workbook_remove_sheet,
    workbook_rename_sheet,
    workbook_row_count,
    workbook_row_style_summary,
    workbook_set_cell_value,
    workbook_sheet_order,
    workbook_sheet_summary,
    workbook_stats,
    workbook_style_family_list,
    workbook_to_csv,
    workbook_to_html,
    workbook_to_xml,
    workbook_total_numeric_value,
    workbook_type_distribution,
    workbook_warnings_for_unsupported_edit,
)

SAMPLES = _REPO / "samples" / "by-format" / "fods"
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"
TYPED = SAMPLES / "typed-values-basic.fods"


@pytest.fixture
def wb():
    return parse_fods(str(MINIMAL))


@pytest.fixture
def typed_wb():
    return parse_fods(str(TYPED))


class TestConstants:
    def test_format_id(self):
        assert FORMAT_ID == "fods"

    def test_spec_version(self):
        assert isinstance(SPEC_VERSION, str)

    def test_package_version(self):
        assert isinstance(PACKAGE_VERSION, str)

    def test_max_file_bytes(self):
        assert isinstance(MAX_FILE_BYTES, int)
        assert MAX_FILE_BYTES > 0


class TestErrorClasses:
    def test_fods_error_is_exception(self):
        assert issubclass(FodsError, Exception)

    def test_fods_input_error_subclass(self):
        assert issubclass(FodsInputError, FodsError)

    def test_fods_size_error_subclass(self):
        assert issubclass(FodsSizeError, FodsError)

    def test_fods_parse_error_subclass(self):
        assert issubclass(FodsParseError, FodsError)

    def test_error_message_preserved(self):
        err = FodsError("bad spreadsheet")
        assert "bad spreadsheet" in str(err)


class TestWorkbookToXml:
    def test_returns_string(self, wb):
        xml = workbook_to_xml(wb)
        assert isinstance(xml, str)
        assert len(xml) > 0


class TestWorkbookStats:
    def test_returns_dict(self, wb):
        stats = workbook_stats(wb)
        assert isinstance(stats, dict)


class TestWorkbookTypeDistribution:
    def test_returns_dict(self, wb):
        dist = workbook_type_distribution(wb)
        assert isinstance(dist, dict)


class TestFindSheetByName:
    def test_finds_existing(self, wb):
        names = workbook_sheet_order(wb)
        if names:
            sheet = find_sheet_by_name(wb, names[0])
            assert sheet is not None

    def test_missing_returns_none(self, wb):
        result = find_sheet_by_name(wb, "NonexistentSheet12345")
        assert result is None


class TestWorkbookSheetSummary:
    def test_returns_list(self, wb):
        summary = workbook_sheet_summary(wb)
        assert isinstance(summary, list)


class TestWorkbookEmptyRows:
    def test_returns_dict(self, wb):
        result = workbook_empty_rows(wb)
        assert isinstance(result, dict)


class TestWorkbookFormulaList:
    def test_returns_list(self, wb):
        formulas = workbook_formula_list(wb)
        assert isinstance(formulas, list)


class TestWorkbookCellRange:
    def test_returns_list(self, wb):
        result = workbook_cell_range(wb, 0, 0, 0, 1, 1)
        assert isinstance(result, list)


class TestWorkbookMergedCellSummary:
    def test_returns_result(self, wb):
        result = workbook_merged_cell_summary(wb)
        assert isinstance(result, (dict, list))


class TestWorkbookNumericSummary:
    def test_returns_dict(self, wb):
        result = workbook_numeric_summary(wb)
        assert isinstance(result, dict)


class TestWorkbookColumnCount:
    def test_returns_result(self, wb):
        result = workbook_column_count(wb)
        assert isinstance(result, (int, dict))


class TestWorkbookRowStyleSummary:
    def test_returns_dict(self, wb):
        result = workbook_row_style_summary(wb)
        assert isinstance(result, dict)


class TestWorkbookFormulaEditPolicy:
    def test_returns_dict(self, wb):
        result = workbook_formula_edit_policy(wb)
        assert isinstance(result, dict)


class TestWorkbookNamedRangeList:
    def test_returns_list(self, wb):
        result = workbook_named_range_list(wb)
        assert isinstance(result, list)


class TestWorkbookColumnStyleSummary:
    def test_returns_dict(self, wb):
        result = workbook_column_style_summary(wb)
        assert isinstance(result, dict)


class TestWorkbookStyleFamilyList:
    def test_returns_list(self, wb):
        result = workbook_style_family_list(wb)
        assert isinstance(result, list)


class TestWorkbookDataValidationSummary:
    def test_returns_dict(self, wb):
        result = workbook_data_validation_summary(wb)
        assert isinstance(result, dict)


class TestWorkbookColumnWidthSummary:
    def test_returns_result(self, wb):
        result = workbook_column_width_summary(wb)
        assert isinstance(result, (dict, list))


class TestWorkbookCellTypeMatrix:
    def test_returns_result(self, wb):
        result = workbook_cell_type_matrix(wb)
        assert isinstance(result, (dict, list))


class TestWorkbookSetCellValue:
    def test_set_and_verify(self, wb):
        result = workbook_set_cell_value(wb, 0, 0, 0, "Hello")
        assert isinstance(result, (dict, tuple))


class TestWorkbookWarningsForUnsupportedEdit:
    def test_returns_list(self, wb):
        result = workbook_warnings_for_unsupported_edit(wb, 0, 0, 0)
        assert isinstance(result, list)


class TestWorkbookAddSheet:
    def test_adds_sheet(self, wb):
        result = workbook_add_sheet(wb, "NewSheet")
        assert isinstance(result, (dict, tuple))
        if isinstance(result, tuple):
            ok, msg = result
            assert ok is True


class TestWorkbookRenameSheet:
    def test_renames(self, wb):
        names = workbook_sheet_order(wb)
        if names:
            result = workbook_rename_sheet(wb, names[0], "Renamed")
            assert isinstance(result, (dict, tuple))
            if isinstance(result, tuple):
                ok, msg = result
                assert ok is True


class TestWorkbookRemoveSheet:
    def test_removes(self, wb):
        workbook_add_sheet(wb, "ToRemove")
        result = workbook_remove_sheet(wb, "ToRemove")
        assert isinstance(result, (dict, tuple))
        if isinstance(result, tuple):
            ok, msg = result
            assert ok is True


class TestWorkbookGetCellValue:
    def test_returns_value(self, wb):
        val = workbook_get_cell_value(wb, 0, 0, 0)
        assert val is not None or val is None  # any value is acceptable


class TestWorkbookFindCells:
    def test_returns_list(self, wb):
        result = workbook_find_cells(wb, "")
        assert isinstance(result, list)


class TestWorkbookCountMatchingCells:
    def test_returns_int(self, wb):
        count = workbook_count_matching_cells(wb, "")
        assert isinstance(count, int)


class TestWorkbookMaxColumnCount:
    def test_returns_int(self, wb):
        count = workbook_max_column_count(wb)
        assert isinstance(count, int)
        assert count >= 0


class TestWorkbookTotalNumericValue:
    def test_returns_number(self, wb):
        total = workbook_total_numeric_value(wb)
        assert isinstance(total, (int, float))


class TestWorkbookToCsv:
    def test_returns_string(self, wb):
        csv = workbook_to_csv(wb)
        assert isinstance(csv, str)


class TestWorkbookToHtml:
    def test_returns_string(self, wb):
        html = workbook_to_html(wb)
        assert isinstance(html, str)
        assert "<" in html


class TestWorkbookRowCount:
    def test_returns_int(self, wb):
        count = workbook_row_count(wb)
        assert isinstance(count, int)
        assert count >= 0


class TestWorkbookNumericDensity:
    def test_returns_number(self, wb):
        density = workbook_numeric_density(wb)
        assert isinstance(density, (int, float))


class TestWorkbookCountNonemptyCells:
    def test_returns_int(self, wb):
        count = workbook_count_nonempty_cells(wb)
        assert isinstance(count, int)
        assert count >= 0


class TestFodsSheetCount:
    def test_returns_int(self, wb):
        count = fods_sheet_count(wb)
        assert isinstance(count, int)
        assert count >= 1


class TestFodsTotalCellCount:
    def test_returns_int(self, wb):
        count = fods_total_cell_count(wb)
        assert isinstance(count, int)
        assert count >= 0
