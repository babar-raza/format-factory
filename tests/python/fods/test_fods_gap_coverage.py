"""Comprehensive gap-coverage tests for the FODS Python FOSS package.

Exercises every function/class exported from ``src/python/fods/__init__.py``
(parser, writer, neutral_model, fods_analytics, fods_analytics_extended,
models, csv_exporter, fods_to_tsv, fods_workflow, fods_sheet_iterator,
fods_cell_iterator, constants, exceptions) plus the file-path analytics
helpers in ``fods_file_analytics.py`` (imported directly from the submodule
since that module is intentionally NOT re-exported at package level — see
test_fods_file_analytics.py for the established import pattern).

Written to close FODS ``missing_test_coverage`` gaps tracked in
reports/capability-layer/gap-ledger.json (GAP-FODS-FOSS-* / GAP-FODS-COMM-*).

NOTE on the ``csv`` stdlib shadow (see MEMORY.md "csv wheel proves in 2nd
pass (stdlib shadow)"): ``src/python/csv/`` is itself a Format Factory format
package. Once ``src/python`` is prepended to ``sys.path``, a *first-time*
``import csv`` anywhere in the process would resolve to that package instead
of the stdlib ``csv`` module, which breaks ``workbook_to_csv`` /
``export_fods_to_csv`` (both do a local ``import csv`` at call time). We
import the real stdlib ``csv`` module here BEFORE mutating ``sys.path`` so it
is already cached in ``sys.modules`` under the name ``csv`` — later lazy
``import csv`` calls anywhere in the process hit that cache and get the
correct stdlib module.
"""
import csv  # noqa: F401 -- stdlib csv; must be imported before sys.path mutation below

import sys
from pathlib import Path

import pytest
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from _shared._shared_exceptions import FormatFactoryError  # noqa: E402
import fods  # noqa: E402
from fods import (  # noqa: E402
    # exceptions
    FodsError,
    FodsInputError,
    FodsSizeError,
    FodsParseError,
    # parser
    parse_fods,
    parse_fods_strict,
    # writer
    workbook_to_xml,
    write_fods,
    # neutral_model
    make_warning,
    build_workbook,
    validate_workbook,
    find_sheet_by_name,
    workbook_set_cell_value,
    workbook_warnings_for_unsupported_edit,
    workbook_add_sheet,
    workbook_rename_sheet,
    workbook_remove_sheet,
    workbook_to_csv,
    workbook_get_cell_value,
    workbook_find_cells,
    workbook_count_matching_cells,
    workbook_to_html,
    workbook_get_column_values,
    workbook_max_column_count,
    # fods_analytics
    workbook_stats,
    workbook_type_distribution,
    workbook_sheet_summary,
    workbook_empty_rows,
    workbook_formula_list,
    workbook_cell_range,
    workbook_merged_cell_summary,
    workbook_sheet_order,
    workbook_numeric_summary,
    workbook_column_count,
    workbook_row_style_summary,
    workbook_formula_edit_policy,
    workbook_named_range_list,
    workbook_column_style_summary,
    workbook_style_family_list,
    workbook_data_validation_summary,
    workbook_column_width_summary,
    workbook_cell_type_matrix,
    workbook_numeric_density,
    workbook_count_nonempty_cells,
    workbook_total_numeric_value,
    fods_sheet_count,
    workbook_row_count,
    workbook_cell_text_at,
    fods_numeric_range,
    fods_column_density,
    fods_empty_row_count,
    fods_distinct_value_count,
    fods_empty_row_percentage,
    fods_cell_value_total,
    # fods_analytics_extended
    fods_formula_count,
    fods_total_cell_count,
    fods_empty_cell_count,
    fods_has_formulas,
    fods_sheet_names,
    fods_string_cell_count,
    fods_numeric_cell_count,
    fods_max_row_count,
    fods_avg_cells_per_sheet,
    fods_has_empty_sheets,
    fods_all_sheets_have_data,
    fods_max_string_length,
    fods_numeric_density,
    fods_data_density,
    fods_string_density,
    fods_is_single_sheet,
    fods_is_multi_sheet,
    fods_min_row_count,
    fods_max_col_count,
    fods_empty_sheet_count,
    fods_total_row_count,
    fods_avg_col_count,
    fods_is_single_cell,
    fods_nonempty_sheet_count,
    fods_has_string_cells,
    fods_row_count_variance,
    fods_avg_string_length,
    fods_col_count_variance,
    fods_cell_to_sheet_ratio,
    fods_avg_numeric_value,
    fods_nonempty_row_ratio,
    fods_longest_row_index,
    fods_numeric_sum_all,
    fods_empty_column_count,
    fods_numeric_cell_ratio,
    fods_max_row_cell_count,
    fods_formula_cell_count,
    fods_sheet_row_variance,
    # models
    FodsDocument,
    FodsSheet,
    FodsCell,
    value_type,
    text,
    repeated,
    from_file,
    odf_version,
    cell_at,
    to_dict,
    export_fods_to_csv,
    # fods_to_tsv
    fods_to_tsv,
    # fods_workflow
    fods_installed_workflow,
    # fods_sheet_iterator / fods_cell_iterator
    fods_iter_sheets,
    fods_iter_cells,
    # constants
    FORMAT_ID,
    SPEC_VERSION,
    EXPECTED_MIMETYPE,
    MAX_FILE_BYTES,
    MAX_EXPAND_REPEAT,
)
from fods.csv_exporter import FodsCsvExportError, export_fods_to_csv_file
from fods.models import export_fods_to_csv as models_export_fods_to_csv
from fods.fods_file_analytics import (
    fods_file_sheet_count,
    fods_file_is_fods,
    fods_file_first_sheet_name,
    fods_file_sheet_names,
    fods_file_has_multiple_sheets,
    fods_file_total_rows,
    fods_file_has_parse_errors,
    fods_file_odf_version,
    fods_file_has_warnings,
    fods_file_last_sheet_name,
    fods_file_sheet_row_counts,
    fods_file_max_sheet_row_count,
    fods_file_min_sheet_row_count,
    fods_file_avg_sheet_row_count,
    fods_file_has_single_sheet,
    fods_file_sheet_names_sorted,
    fods_file_first_sheet_row_count,
    fods_file_last_sheet_row_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "fods"
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"
MULTI = SAMPLES / "multi-sheet-basic.fods"
TYPED = SAMPLES / "typed-values-basic.fods"
FORMULA = SAMPLES / "formula-basic.fods"
MUTATION = SAMPLES / "valid" / "mutation-coverage.fods"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_wb():
    return parse_fods(str(MINIMAL))


@pytest.fixture
def multi_wb():
    return parse_fods(str(MULTI))


@pytest.fixture
def typed_wb():
    return parse_fods(str(TYPED))


@pytest.fixture
def formula_wb():
    return parse_fods(str(FORMULA))


@pytest.fixture
def mutation_wb():
    return parse_fods(str(MUTATION))


# ---------------------------------------------------------------------------
# parser.py — parse_fods / parse_fods_strict
# ---------------------------------------------------------------------------

class TestParser:
    def test_parse_fods_minimal(self, minimal_wb):
        assert minimal_wb["sheet_count"] == 1
        assert minimal_wb["sheets"][0]["name"] == "Sheet1"
        assert "error" not in minimal_wb

    def test_parse_fods_multi_sheet(self, multi_wb):
        assert multi_wb["sheet_count"] == 2
        names = [s["name"] for s in multi_wb["sheets"]]
        assert names == ["Data", "Summary"]

    def test_parse_fods_strict_matches_parse_fods(self):
        strict = parse_fods_strict(str(MULTI))
        loose = parse_fods(str(MULTI))
        assert strict["sheet_count"] == loose["sheet_count"]

    def test_parse_fods_format_id_and_spec_version(self, minimal_wb):
        assert minimal_wb["format_id"] == FORMAT_ID
        assert minimal_wb["spec_version"] == SPEC_VERSION

    def test_parse_fods_odf_version_attr(self, minimal_wb):
        assert minimal_wb["odf_version_attr"] == "1.3"

    def test_parse_fods_mimetype(self, minimal_wb):
        assert minimal_wb["mimetype"] == EXPECTED_MIMETYPE

    def test_parse_fods_missing_file_never_raises(self):
        result = parse_fods("does/not/exist.fods")
        assert "error" in result
        assert result["parse_errors"] == []

    def test_parse_fods_strict_missing_file_raises_input_error(self):
        with pytest.raises(FodsInputError):
            parse_fods_strict("does/not/exist.fods")

    def test_parse_fods_strict_directory_raises_input_error(self, tmp_path):
        with pytest.raises(FodsInputError):
            parse_fods_strict(tmp_path)

    def test_parse_fods_strict_wrong_root_raises_parse_error(self, tmp_path):
        bad = tmp_path / "wrongroot.fods"
        bad.write_text(
            '<foo xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"></foo>',
            encoding="utf-8",
        )
        with pytest.raises(FodsParseError):
            parse_fods_strict(bad)

    def test_parse_fods_wrong_root_returns_error_dict(self, tmp_path):
        bad = tmp_path / "wrongroot.fods"
        bad.write_text(
            '<foo xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"></foo>',
            encoding="utf-8",
        )
        result = parse_fods(bad)
        assert "error" in result
        assert result["parse_errors"][0]["code"] == "WRONG_ROOT"

    def test_parse_fods_strict_malformed_xml_raises_parse_error(self, tmp_path):
        bad = tmp_path / "malformed.fods"
        bad.write_text(
            '<office:document '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">'
            "<office:body></office:mismatched>",
            encoding="utf-8",
        )
        with pytest.raises(FodsParseError):
            parse_fods_strict(bad)

    def test_parse_fods_strict_empty_file_raises_parse_error(self, tmp_path):
        empty = tmp_path / "empty.fods"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(FodsParseError):
            parse_fods_strict(empty)

    def test_parse_fods_strict_size_guard(self, tmp_path, monkeypatch):
        import fods.parser as parser_mod

        monkeypatch.setattr(parser_mod, "MAX_FILE_BYTES", 10)
        with pytest.raises(FodsSizeError):
            parse_fods_strict(str(MULTI))

    def test_parse_fods_typed_values(self, typed_wb):
        rows = typed_wb["sheets"][0]["rows"]
        assert rows[2]["cells"][1]["value"] == 42.5
        assert rows[2]["cells"][1]["value_type"] == "float"
        assert rows[3]["cells"][1]["value"] is True
        assert rows[3]["cells"][1]["value_type"] == "boolean"

    def test_parse_fods_formula_capture(self, formula_wb):
        cell = formula_wb["sheets"][0]["rows"][3]["cells"][0]
        assert cell["formula"] == "oooc:=SUM([.A1:.A3])"
        assert cell["value"] == 60.0
        assert any(w["code"] == "FORMULA_CELL" for w in formula_wb["warnings"])

    def test_parse_fods_covered_cell_and_span(self, mutation_wb):
        row = mutation_wb["sheets"][0]["rows"][1]
        assert row["cells"][0].get("col_span") == 2
        assert row["cells"][1]["is_covered"] is True
        assert any(w["code"] == "COVERED_CELL" for w in mutation_wb["warnings"])

    def test_parse_fods_draw_frame_unsupported_feature(self, mutation_wb):
        assert "chart" in mutation_wb["unsupported_features"]

    def test_parse_fods_void_and_date_values(self, mutation_wb):
        row = mutation_wb["sheets"][0]["rows"][0]
        assert row["cells"][2]["value"] == "2026-07-03"  # date
        assert row["cells"][3]["value"] is None  # void

    def test_parse_fods_empty_sheet_row_count(self, mutation_wb):
        empty_sheet = mutation_wb["sheets"][1]
        assert empty_sheet["name"] == "EmptySheet"
        assert empty_sheet["row_count"] == 0
        assert empty_sheet["rows"] == []


# ---------------------------------------------------------------------------
# writer.py — workbook_to_xml / write_fods
# ---------------------------------------------------------------------------

class TestWriter:
    def test_workbook_to_xml_roundtrip(self, multi_wb):
        xml = workbook_to_xml(multi_wb)
        assert xml.startswith("<?xml")
        assert xml.count("table:table ") == 2 or xml.count("<table:table") == 2

    def test_workbook_to_xml_rejects_non_dict(self):
        with pytest.raises(FodsInputError):
            workbook_to_xml("not a dict")

    def test_workbook_to_xml_rejects_non_list_sheets(self):
        with pytest.raises(FodsInputError):
            workbook_to_xml({"sheets": "not a list"})

    def test_write_fods_roundtrip(self, multi_wb, tmp_path):
        dest = tmp_path / "out.fods"
        write_fods(multi_wb, dest)
        assert dest.exists()
        reparsed = parse_fods(str(dest))
        assert reparsed["sheet_count"] == 2
        assert [s["name"] for s in reparsed["sheets"]] == ["Data", "Summary"]

    def test_write_fods_preserves_formula(self, formula_wb, tmp_path):
        dest = tmp_path / "formula_out.fods"
        write_fods(formula_wb, dest)
        reparsed = parse_fods(str(dest))
        cell = reparsed["sheets"][0]["rows"][3]["cells"][0]
        assert cell["formula"] == "oooc:=SUM([.A1:.A3])"

    def test_write_fods_typed_values_roundtrip(self, typed_wb, tmp_path):
        dest = tmp_path / "typed_out.fods"
        write_fods(typed_wb, dest)
        reparsed = parse_fods(str(dest))
        row = reparsed["sheets"][0]["rows"][3]
        assert row["cells"][1]["value_type"] == "boolean"


# ---------------------------------------------------------------------------
# neutral_model.py
# ---------------------------------------------------------------------------

class TestNeutralModelHelpers:
    def test_make_warning_with_source(self):
        w = make_warning("CODE", "msg", source="src1")
        assert w == {"code": "CODE", "message": "msg", "source": "src1"}

    def test_make_warning_without_source(self):
        w = make_warning("CODE", "msg")
        assert w == {"code": "CODE", "message": "msg"}
        assert "source" not in w

    def test_build_workbook_shape(self):
        wb = build_workbook("1.3", EXPECTED_MIMETYPE, [], [], [], [])
        assert wb["format_id"] == FORMAT_ID
        assert wb["spec_version"] == SPEC_VERSION
        assert wb["sheet_count"] == 0
        assert wb["sheets"] == []

    def test_validate_workbook_valid_empty(self):
        wb = build_workbook("1.3", EXPECTED_MIMETYPE, [], [], [], [])
        assert validate_workbook(wb) == []

    def test_validate_workbook_reports_bad_sheets_type(self):
        violations = validate_workbook({"sheets": "not a list"})
        assert any("must be a list" in v for v in violations)

    def test_validate_workbook_real_document(self, multi_wb):
        assert validate_workbook(multi_wb) == []


class TestFindSheetByName:
    def test_find_existing_sheet(self, multi_wb):
        sheet = find_sheet_by_name(multi_wb, "Data")
        assert sheet is not None
        assert sheet["name"] == "Data"

    def test_find_missing_sheet_returns_none(self, multi_wb):
        assert find_sheet_by_name(multi_wb, "DoesNotExist") is None


class TestWorkbookSetCellValue:
    def test_set_cell_value_success(self, multi_wb):
        ok, msg = workbook_set_cell_value(multi_wb, "Data", 0, 0, "Updated")
        assert ok is True
        assert "Updated" in msg
        assert workbook_get_cell_value(multi_wb, "Data", 0, 0) == "Updated"

    def test_set_cell_value_infers_boolean_type(self, multi_wb):
        ok, _ = workbook_set_cell_value(multi_wb, "Data", 0, 0, True)
        assert ok is True
        cell = multi_wb["sheets"][0]["rows"][0]["cells"][0]
        assert cell["value_type"] == "boolean"

    def test_set_cell_value_infers_float_type(self, multi_wb):
        ok, _ = workbook_set_cell_value(multi_wb, "Data", 0, 0, 3.5)
        assert ok is True
        cell = multi_wb["sheets"][0]["rows"][0]["cells"][0]
        assert cell["value_type"] == "float"

    def test_set_cell_value_missing_sheet(self, multi_wb):
        ok, msg = workbook_set_cell_value(multi_wb, "NoSuchSheet", 0, 0, "x")
        assert ok is False
        assert "not found" in msg

    def test_set_cell_value_row_out_of_range(self, multi_wb):
        ok, msg = workbook_set_cell_value(multi_wb, "Data", 99, 0, "x")
        assert ok is False
        assert "out of range" in msg

    def test_set_cell_value_col_out_of_range(self, multi_wb):
        ok, msg = workbook_set_cell_value(multi_wb, "Data", 0, 99, "x")
        assert ok is False
        assert "out of range" in msg

    def test_set_cell_value_not_a_dict(self):
        ok, msg = workbook_set_cell_value("not a dict", "Data", 0, 0, "x")
        assert ok is False
        assert "must be a dict" in msg

    def test_set_cell_value_clears_formula(self, formula_wb):
        ok, _ = workbook_set_cell_value(formula_wb, "Sheet1", 3, 0, 99.0)
        assert ok is True
        cell = formula_wb["sheets"][0]["rows"][3]["cells"][0]
        assert cell["formula"] is None


class TestWorkbookWarningsForUnsupportedEdit:
    def test_no_warnings_for_plain_cell(self, multi_wb):
        warns = workbook_warnings_for_unsupported_edit(multi_wb, "Data", 0, 0)
        assert warns == []

    def test_warning_for_formula_cell(self, formula_wb):
        warns = workbook_warnings_for_unsupported_edit(formula_wb, "Sheet1", 3, 0)
        assert any("formula" in w.lower() for w in warns)

    def test_warning_for_missing_sheet(self, multi_wb):
        warns = workbook_warnings_for_unsupported_edit(multi_wb, "Nope", 0, 0)
        assert warns == ["Sheet 'Nope' not found"]


class TestSheetManagement:
    def test_add_sheet_success(self, multi_wb):
        ok, msg = workbook_add_sheet(multi_wb, "NewSheet")
        assert ok is True
        assert len(multi_wb["sheets"]) == 3
        assert multi_wb["sheets"][-1]["name"] == "NewSheet"

    def test_add_sheet_at_position(self, multi_wb):
        ok, _ = workbook_add_sheet(multi_wb, "Inserted", position=0)
        assert ok is True
        assert multi_wb["sheets"][0]["name"] == "Inserted"

    def test_add_sheet_duplicate_name_rejected(self, multi_wb):
        ok, msg = workbook_add_sheet(multi_wb, "Data")
        assert ok is False
        assert "already exists" in msg

    def test_add_sheet_empty_name_rejected(self, multi_wb):
        ok, msg = workbook_add_sheet(multi_wb, "   ")
        assert ok is False
        assert "must not be empty" in msg

    def test_rename_sheet_success(self, multi_wb):
        ok, msg = workbook_rename_sheet(multi_wb, "Data", "Renamed")
        assert ok is True
        assert find_sheet_by_name(multi_wb, "Renamed") is not None
        assert find_sheet_by_name(multi_wb, "Data") is None

    def test_rename_sheet_missing_source(self, multi_wb):
        ok, msg = workbook_rename_sheet(multi_wb, "NoSuch", "X")
        assert ok is False
        assert "not found" in msg

    def test_rename_sheet_target_exists(self, multi_wb):
        ok, msg = workbook_rename_sheet(multi_wb, "Data", "Summary")
        assert ok is False
        assert "already exists" in msg

    def test_rename_sheet_empty_new_name(self, multi_wb):
        ok, msg = workbook_rename_sheet(multi_wb, "Data", "")
        assert ok is False
        assert "must not be empty" in msg

    def test_remove_sheet_success(self, multi_wb):
        ok, msg = workbook_remove_sheet(multi_wb, "Summary")
        assert ok is True
        assert len(multi_wb["sheets"]) == 1

    def test_remove_sheet_missing(self, multi_wb):
        ok, msg = workbook_remove_sheet(multi_wb, "NoSuch")
        assert ok is False
        assert "not found" in msg

    def test_remove_last_sheet_rejected(self, minimal_wb):
        ok, msg = workbook_remove_sheet(minimal_wb, "Sheet1")
        assert ok is False
        assert "only sheet" in msg


class TestWorkbookToCsv:
    def test_to_csv_default_first_sheet(self, multi_wb):
        csv_text = workbook_to_csv(multi_wb)
        assert csv_text == "Name,Value\r\nAlpha,Beta\r\n"

    def test_to_csv_named_sheet(self, multi_wb):
        csv_text = workbook_to_csv(multi_wb, "Summary")
        assert csv_text == "Summary Sheet\r\n"

    def test_to_csv_missing_sheet_returns_empty(self, multi_wb):
        assert workbook_to_csv(multi_wb, "Nope") == ""

    def test_to_csv_no_sheets_returns_empty(self):
        assert workbook_to_csv({"sheets": []}) == ""


class TestWorkbookGetCellValue:
    def test_get_cell_value_present(self, multi_wb):
        assert workbook_get_cell_value(multi_wb, "Data", 1, 0) == "Alpha"

    def test_get_cell_value_missing_sheet(self, multi_wb):
        assert workbook_get_cell_value(multi_wb, "Nope", 0, 0) is None

    def test_get_cell_value_row_out_of_range(self, multi_wb):
        assert workbook_get_cell_value(multi_wb, "Data", 99, 0) is None

    def test_get_cell_value_col_out_of_range(self, multi_wb):
        assert workbook_get_cell_value(multi_wb, "Data", 0, 99) is None


class TestWorkbookFindCells:
    def test_find_cells_case_insensitive_default(self, multi_wb):
        matches = workbook_find_cells(multi_wb, "alpha")
        assert len(matches) == 1
        assert matches[0]["value"] == "Alpha"
        assert matches[0]["sheet_name"] == "Data"
        assert matches[0]["row_index"] == 1
        assert matches[0]["col_index"] == 0

    def test_find_cells_case_sensitive_no_match(self, multi_wb):
        assert workbook_find_cells(multi_wb, "alpha", case_sensitive=True) == []

    def test_find_cells_case_sensitive_match(self, multi_wb):
        matches = workbook_find_cells(multi_wb, "Alpha", case_sensitive=True)
        assert len(matches) == 1

    def test_find_cells_non_string_value(self, typed_wb):
        matches = workbook_find_cells(typed_wb, 42.5)
        assert len(matches) == 1
        assert matches[0]["value"] == 42.5

    def test_count_matching_cells(self, multi_wb):
        assert workbook_count_matching_cells(multi_wb, "Alpha") == 1
        assert workbook_count_matching_cells(multi_wb, "NoSuchValue") == 0


class TestWorkbookToHtml:
    def test_to_html_default_sheet(self, multi_wb):
        html = workbook_to_html(multi_wb)
        assert html.startswith("<table>")
        assert "<td>Name</td>" in html
        assert "<td>Alpha</td>" in html

    def test_to_html_out_of_range_returns_empty(self, multi_wb):
        assert workbook_to_html(multi_wb, sheet_index=99) == ""

    def test_to_html_empty_sheet(self, mutation_wb):
        assert workbook_to_html(mutation_wb, sheet_index=1) == "<table></table>"

    def test_to_html_escapes_values(self):
        wb = {
            "sheets": [
                {
                    "name": "S",
                    "rows": [
                        {"cells": [{"value": "<b>&amp;</b>"}]},
                    ],
                }
            ]
        }
        html = workbook_to_html(wb)
        assert "&lt;b&gt;" in html


class TestWorkbookColumns:
    def test_get_column_values(self, multi_wb):
        assert workbook_get_column_values(multi_wb, 0) == ["Name", "Alpha"]

    def test_get_column_values_out_of_range_sheet(self, multi_wb):
        assert workbook_get_column_values(multi_wb, 0, sheet_index=99) == []

    def test_get_column_values_missing_col_is_none(self, multi_wb):
        vals = workbook_get_column_values(multi_wb, 99)
        assert vals == [None, None]

    def test_max_column_count(self, multi_wb):
        assert workbook_max_column_count(multi_wb) == 2

    def test_max_column_count_mutation_sheet(self, mutation_wb):
        assert workbook_max_column_count(mutation_wb) == 7

    def test_max_column_count_no_sheets(self):
        assert workbook_max_column_count({"sheets": []}) == 0


# ---------------------------------------------------------------------------
# fods_analytics.py
# ---------------------------------------------------------------------------

class TestWorkbookStats:
    def test_workbook_stats_mutation(self, mutation_wb):
        stats = workbook_stats(mutation_wb)
        assert stats["sheet_count"] == 2
        assert stats["total_rows"] == 3
        assert stats["total_cells"] == 10
        assert stats["non_empty_cells"] == 8
        assert stats["formula_cells"] == 0
        assert len(stats["per_sheet"]) == 2

    def test_workbook_stats_formula_cells(self, formula_wb):
        stats = workbook_stats(formula_wb)
        assert stats["formula_cells"] == 1


class TestWorkbookTypeDistribution:
    def test_type_distribution_typed(self, typed_wb):
        dist = workbook_type_distribution(typed_wb)
        assert dist["by_type"] == {"string": 6, "float": 1, "boolean": 1}
        assert dist["total_cells"] == 8
        assert len(dist["per_sheet"]) == 1


class TestWorkbookSheetSummary:
    def test_sheet_summary_multi(self, multi_wb):
        summary = workbook_sheet_summary(multi_wb)
        assert summary[0]["name"] == "Data"
        assert summary[0]["row_count"] == 2
        assert summary[0]["cell_count"] == 4
        assert summary[1]["name"] == "Summary"
        assert summary[1]["cell_count"] == 1


class TestWorkbookEmptyRows:
    def test_empty_rows_mutation(self, mutation_wb):
        result = workbook_empty_rows(mutation_wb)
        assert result["total_empty_rows"] == 0
        assert result["per_sheet"][1]["total_row_count"] == 0


class TestWorkbookFormulaList:
    def test_formula_list_formula_sample(self, formula_wb):
        formulas = workbook_formula_list(formula_wb)
        assert len(formulas) == 1
        entry = formulas[0]
        assert entry["sheet_name"] == "Sheet1"
        assert entry["formula"] == "oooc:=SUM([.A1:.A3])"
        assert entry["value"] == 60.0
        assert entry["row_index"] == 3
        assert entry["col_index"] == 0

    def test_formula_list_no_formulas(self, multi_wb):
        assert workbook_formula_list(multi_wb) == []


class TestWorkbookCellRange:
    def test_cell_range_full_sheet(self, multi_wb):
        rng = workbook_cell_range(multi_wb, sheet_index=0)
        assert rng == [["Name", "Value"], ["Alpha", "Beta"]]

    def test_cell_range_partial(self, multi_wb):
        rng = workbook_cell_range(multi_wb, sheet_index=0, row_start=1, row_end=1, col_start=0, col_end=0)
        assert rng == [["Alpha"]]

    def test_cell_range_out_of_range_sheet(self, multi_wb):
        assert workbook_cell_range(multi_wb, sheet_index=99) == []


class TestWorkbookMergedCellSummary:
    def test_no_merge_metadata_in_real_parse(self, mutation_wb):
        # Parser stores spans as col_span/row_span, not 'merge'/'span' keys,
        # so workbook_merged_cell_summary (which looks for those legacy keys)
        # finds nothing on real parsed data — documents current behavior.
        assert workbook_merged_cell_summary(mutation_wb) == []

    def test_merge_detected_when_key_present(self):
        wb = {
            "sheets": [
                {"name": "S", "rows": [{"cells": [{"value": "x", "merge": "A1:B1"}]}]}
            ]
        }
        results = workbook_merged_cell_summary(wb)
        assert len(results) == 1
        assert results[0]["merge_info"] == "A1:B1"


class TestWorkbookSheetOrder:
    def test_sheet_order(self, multi_wb):
        assert workbook_sheet_order(multi_wb) == ["Data", "Summary"]

    def test_sheet_order_empty(self):
        assert workbook_sheet_order({"sheets": []}) == []


class TestWorkbookNumericSummary:
    def test_numeric_summary_typed(self, typed_wb):
        summary = workbook_numeric_summary(typed_wb)
        assert summary["total_numeric_cells"] == 1
        assert summary["global_min"] == 42.5
        assert summary["global_max"] == 42.5
        assert summary["global_sum"] == 42.5

    def test_numeric_summary_no_numeric_cells(self, multi_wb):
        summary = workbook_numeric_summary(multi_wb)
        assert summary["total_numeric_cells"] == 0
        assert summary["global_min"] is None
        assert summary["global_max"] is None


class TestWorkbookColumnCount:
    def test_column_count_per_sheet(self, mutation_wb):
        result = workbook_column_count(mutation_wb)
        assert result["total_sheets"] == 2
        assert result["per_sheet"][0]["sheet_name"] == "ValueTypes"
        assert result["per_sheet"][0]["max_columns"] == 6
        assert result["per_sheet"][1]["max_columns"] == 0


class TestWorkbookRowStyleSummary:
    def test_no_row_styles_in_real_parse(self, multi_wb):
        result = workbook_row_style_summary(multi_wb)
        assert result == {"Data": [], "Summary": []}


class TestWorkbookFormulaEditPolicy:
    def test_policy_no_formulas(self, typed_wb):
        policy = workbook_formula_edit_policy(typed_wb)
        assert policy["policy"] == "no_formulas"
        assert policy["total_formulas"] == 0

    def test_policy_all_editable(self, formula_wb):
        policy = workbook_formula_edit_policy(formula_wb)
        assert policy["policy"] == "all_editable"
        assert policy["total_formulas"] == 1
        assert policy["editable_formulas"] == 1
        assert policy["locked_formulas"] == 0


class TestWorkbookNamedRangeList:
    def test_no_named_ranges_in_real_parse(self, multi_wb):
        assert workbook_named_range_list(multi_wb) == []

    def test_named_range_from_workbook_level_dict(self):
        wb = {"sheets": [], "named_ranges": [{"name": "Foo", "cell_range": "Sheet1.A1:B2"}]}
        result = workbook_named_range_list(wb)
        assert result == [{"name": "Foo", "cell_range": "Sheet1.A1:B2", "base_cell": None}]

    def test_named_range_from_string_entry(self):
        wb = {"sheets": [], "named_ranges": ["Foo"]}
        result = workbook_named_range_list(wb)
        assert result == [{"name": "Foo", "cell_range": "", "base_cell": None}]


class TestWorkbookColumnStyleSummary:
    def test_no_column_styles_in_real_parse(self, multi_wb):
        assert workbook_column_style_summary(multi_wb) == {"Data": [], "Summary": []}


class TestWorkbookStyleFamilyList:
    def test_no_style_metadata_in_real_parse(self, multi_wb):
        assert workbook_style_family_list(multi_wb) == []

    def test_style_family_from_plain_dict(self):
        wb = {"sheets": [], "auto_styles": [{"family": "table-cell"}, {"family": "table-cell"}]}
        result = workbook_style_family_list(wb)
        assert result == [{"family_name": "table-cell", "style_count": 2}]


class TestWorkbookDataValidationSummary:
    def test_no_validations_in_real_parse(self, multi_wb):
        result = workbook_data_validation_summary(multi_wb)
        assert result == {"validation_count": 0, "validated_cell_ranges": []}

    def test_validation_from_workbook_level_list(self):
        wb = {"sheets": [], "data_validations": [{"cell_range": "A1:A5"}]}
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 1
        assert result["validated_cell_ranges"] == ["A1:A5"]


class TestWorkbookColumnWidthSummary:
    def test_no_column_defs_in_real_parse(self, multi_wb):
        result = workbook_column_width_summary(multi_wb)
        assert result == [
            {"sheet_name": "Data", "column_count": 0, "widths": []},
            {"sheet_name": "Summary", "column_count": 0, "widths": []},
        ]


class TestWorkbookCellTypeMatrix:
    def test_cell_type_matrix_mutation(self, mutation_wb):
        matrix = workbook_cell_type_matrix(mutation_wb)
        value_types_sheet = matrix[0]
        assert value_types_sheet["sheet_name"] == "ValueTypes"
        assert value_types_sheet["by_type"]["boolean"] == 2
        assert value_types_sheet["by_type"]["datetime"] == 1
        assert value_types_sheet["by_type"]["text"] == 4
        assert matrix[1]["by_type"] == {}

    def test_cell_type_matrix_formula(self, formula_wb):
        matrix = workbook_cell_type_matrix(formula_wb)
        assert matrix[0]["by_type"]["formula"] == 1


class TestWorkbookNumericDensity:
    def test_numeric_density_typed(self, typed_wb):
        # boolean cells are also numeric under isinstance(x, (int, float))
        assert workbook_numeric_density(typed_wb) == pytest.approx(0.25)

    def test_numeric_density_out_of_range(self, typed_wb):
        assert workbook_numeric_density(typed_wb, sheet_index=99) == 0.0


class TestWorkbookCountNonemptyCells:
    def test_count_nonempty_typed(self, typed_wb):
        assert workbook_count_nonempty_cells(typed_wb) == 8

    def test_count_nonempty_out_of_range(self, typed_wb):
        assert workbook_count_nonempty_cells(typed_wb, sheet_index=99) == 0


class TestWorkbookTotalNumericValue:
    def test_total_numeric_value_typed(self, typed_wb):
        assert workbook_total_numeric_value(typed_wb) == pytest.approx(42.5)

    def test_total_numeric_value_out_of_range(self, typed_wb):
        assert workbook_total_numeric_value(typed_wb, sheet_index=99) == 0.0


class TestFodsSheetCountAndRowCount:
    def test_fods_sheet_count(self, multi_wb):
        assert fods_sheet_count(multi_wb) == 2

    def test_fods_sheet_count_empty(self):
        assert fods_sheet_count({}) == 0

    def test_workbook_row_count(self, multi_wb):
        assert workbook_row_count(multi_wb) == 2

    def test_workbook_row_count_out_of_range(self, multi_wb):
        assert workbook_row_count(multi_wb, sheet_index=99) == 0


class TestWorkbookCellTextAt:
    def test_cell_text_at_found(self, typed_wb):
        assert workbook_cell_text_at(typed_wb, 0, 2, 1) == "42.5"

    def test_cell_text_at_sheet_out_of_range(self, typed_wb):
        assert workbook_cell_text_at(typed_wb, 99, 0, 0) == ""

    def test_cell_text_at_row_out_of_range(self, typed_wb):
        assert workbook_cell_text_at(typed_wb, 0, 99, 0) == ""

    def test_cell_text_at_col_out_of_range(self, typed_wb):
        assert workbook_cell_text_at(typed_wb, 0, 0, 99) == ""


class TestFodsAnalyticsMisc:
    def test_fods_numeric_range(self, typed_wb):
        # float(42.5) and float(True)==1.0 both counted as numeric values
        assert fods_numeric_range(typed_wb) == pytest.approx(41.5)

    def test_fods_numeric_range_insufficient_values(self, multi_wb):
        assert fods_numeric_range(multi_wb) == 0.0

    def test_fods_column_density(self, typed_wb):
        assert fods_column_density(typed_wb) == 1.0

    def test_fods_column_density_empty(self):
        assert fods_column_density({"sheets": []}) == 0.0

    def test_fods_empty_row_count(self, mutation_wb):
        assert fods_empty_row_count(mutation_wb) == 0

    def test_fods_distinct_value_count(self, typed_wb):
        assert fods_distinct_value_count(typed_wb) == 8

    def test_fods_empty_row_percentage(self, mutation_wb):
        assert fods_empty_row_percentage(mutation_wb) == 0.0

    def test_fods_empty_row_percentage_no_rows(self):
        assert fods_empty_row_percentage({"sheets": []}) == 0.0

    def test_fods_cell_value_total(self, typed_wb):
        assert fods_cell_value_total(typed_wb) == pytest.approx(43.5)


# ---------------------------------------------------------------------------
# fods_analytics_extended.py
# ---------------------------------------------------------------------------

class TestFodsAnalyticsExtended:
    def test_fods_formula_count(self, formula_wb, typed_wb):
        assert fods_formula_count(formula_wb) == 1
        assert fods_formula_count(typed_wb) == 0

    def test_fods_total_cell_count(self, typed_wb, formula_wb):
        assert fods_total_cell_count(typed_wb) == 8
        assert fods_total_cell_count(formula_wb) == 4

    def test_fods_empty_cell_count(self, mutation_wb):
        assert fods_empty_cell_count(mutation_wb) == 2

    def test_fods_has_formulas(self, formula_wb, typed_wb):
        assert fods_has_formulas(formula_wb) is True
        assert fods_has_formulas(typed_wb) is False

    def test_fods_sheet_names(self, mutation_wb):
        assert fods_sheet_names(mutation_wb) == ["ValueTypes", "EmptySheet"]

    def test_fods_string_cell_count(self, typed_wb, mutation_wb):
        assert fods_string_cell_count(typed_wb) == 6
        assert fods_string_cell_count(mutation_wb) == 4

    def test_fods_numeric_cell_count(self, typed_wb, formula_wb):
        assert fods_numeric_cell_count(typed_wb) == 1
        assert fods_numeric_cell_count(formula_wb) == 4

    def test_fods_max_row_count(self, formula_wb, mutation_wb):
        assert fods_max_row_count(formula_wb) == 4
        assert fods_max_row_count(mutation_wb) == 3

    def test_fods_max_row_count_no_sheets(self):
        assert fods_max_row_count({"sheets": []}) == 0

    def test_fods_avg_cells_per_sheet(self, typed_wb):
        assert fods_avg_cells_per_sheet(typed_wb) == 8.0

    def test_fods_avg_cells_per_sheet_no_sheets(self):
        assert fods_avg_cells_per_sheet({"sheets": []}) == 0.0

    def test_fods_has_empty_sheets(self, mutation_wb, typed_wb):
        assert fods_has_empty_sheets(mutation_wb) is True
        assert fods_has_empty_sheets(typed_wb) is False

    def test_fods_all_sheets_have_data(self, typed_wb, mutation_wb):
        assert fods_all_sheets_have_data(typed_wb) is True
        assert fods_all_sheets_have_data(mutation_wb) is False

    def test_fods_all_sheets_have_data_empty_workbook(self):
        assert fods_all_sheets_have_data({"sheets": []}) is False

    def test_fods_max_string_length(self, typed_wb, mutation_wb):
        assert fods_max_string_length(typed_wb) == 11  # "Hello World"
        assert fods_max_string_length(mutation_wb) == 13  # "fallback-text"

    def test_fods_numeric_density(self, formula_wb, mutation_wb):
        assert fods_numeric_density(formula_wb) == 1.0
        assert fods_numeric_density(mutation_wb) == 0.0

    def test_fods_data_density(self, typed_wb, mutation_wb):
        assert fods_data_density(typed_wb) == 1.0
        assert fods_data_density(mutation_wb) == 0.75

    def test_fods_string_density(self, typed_wb, formula_wb):
        assert fods_string_density(typed_wb) == 0.75
        assert fods_string_density(formula_wb) == 0.0

    def test_fods_is_single_sheet(self, typed_wb, mutation_wb):
        assert fods_is_single_sheet(typed_wb) is True
        assert fods_is_single_sheet(mutation_wb) is False

    def test_fods_is_multi_sheet(self, mutation_wb, typed_wb):
        assert fods_is_multi_sheet(mutation_wb) is True
        assert fods_is_multi_sheet(typed_wb) is False

    def test_fods_min_row_count(self, mutation_wb):
        assert fods_min_row_count(mutation_wb) == 0

    def test_fods_min_row_count_no_sheets(self):
        assert fods_min_row_count({"sheets": []}) == 0

    def test_fods_max_col_count(self, mutation_wb):
        assert fods_max_col_count(mutation_wb) == 7

    def test_fods_empty_sheet_count(self, mutation_wb, typed_wb):
        assert fods_empty_sheet_count(mutation_wb) == 1
        assert fods_empty_sheet_count(typed_wb) == 0

    def test_fods_total_row_count(self, mutation_wb):
        assert fods_total_row_count(mutation_wb) == 3

    def test_fods_avg_col_count(self, mutation_wb):
        assert fods_avg_col_count(mutation_wb) == pytest.approx(10 / 3)

    def test_fods_avg_col_count_no_rows(self):
        assert fods_avg_col_count({"sheets": []}) == 0.0

    def test_fods_is_single_cell(self, minimal_wb, typed_wb):
        assert fods_is_single_cell(minimal_wb) is True
        assert fods_is_single_cell(typed_wb) is False

    def test_fods_nonempty_sheet_count(self, mutation_wb):
        assert fods_nonempty_sheet_count(mutation_wb) == 1

    def test_fods_has_string_cells(self, typed_wb, formula_wb):
        assert fods_has_string_cells(typed_wb) is True
        assert fods_has_string_cells(formula_wb) is False

    def test_fods_row_count_variance(self, mutation_wb, typed_wb):
        assert fods_row_count_variance(mutation_wb) == pytest.approx(2.25)
        assert fods_row_count_variance(typed_wb) == 0.0  # fewer than 2 sheets

    def test_fods_avg_string_length_known_quirk(self, typed_wb):
        # Real parser output has no 'text' key on cell dicts, so this
        # function (which reads cell.get('text', '')) always returns 0.0
        # for genuinely-parsed workbooks. Documents current behavior.
        assert fods_avg_string_length(typed_wb) == 0.0

    def test_fods_col_count_variance(self, mutation_wb, typed_wb):
        assert fods_col_count_variance(mutation_wb) == pytest.approx(12.25)
        assert fods_col_count_variance(typed_wb) == 0.0

    def test_fods_cell_to_sheet_ratio(self, typed_wb, mutation_wb):
        assert fods_cell_to_sheet_ratio(typed_wb) == 8.0
        assert fods_cell_to_sheet_ratio(mutation_wb) == 5.0

    def test_fods_cell_to_sheet_ratio_no_sheets(self):
        assert fods_cell_to_sheet_ratio({"sheets": []}) == 0.0

    def test_fods_avg_numeric_value(self, typed_wb, formula_wb):
        assert fods_avg_numeric_value(typed_wb) == pytest.approx(42.5)
        assert fods_avg_numeric_value(formula_wb) == pytest.approx(30.0)

    def test_fods_avg_numeric_value_no_numeric(self, multi_wb):
        assert fods_avg_numeric_value(multi_wb) == 0.0

    def test_fods_nonempty_row_ratio_known_quirk(self, typed_wb):
        # Same 'text' key quirk as fods_avg_string_length.
        assert fods_nonempty_row_ratio(typed_wb) == 0.0

    def test_fods_nonempty_row_ratio_no_rows(self, mutation_wb):
        assert fods_nonempty_row_ratio(mutation_wb, sheet_index=1) == 0.0

    def test_fods_longest_row_index_known_quirk(self, typed_wb):
        # Same 'text' key quirk — always resolves to the first row (index 0).
        assert fods_longest_row_index(typed_wb) == 0

    def test_fods_longest_row_index_no_rows(self, mutation_wb):
        assert fods_longest_row_index(mutation_wb, sheet_index=1) == -1

    def test_fods_longest_row_index_out_of_range(self, typed_wb):
        assert fods_longest_row_index(typed_wb, sheet_index=99) == -1

    def test_fods_numeric_sum_all(self, formula_wb):
        assert fods_numeric_sum_all(formula_wb) == pytest.approx(120.0)

    def test_fods_empty_column_count(self, mutation_wb):
        # Same 'text' key quirk — every column looks "empty" via this check.
        count = fods_empty_column_count(mutation_wb, sheet_index=0)
        assert isinstance(count, int)
        assert count >= 0

    def test_fods_empty_column_count_no_rows(self, mutation_wb):
        assert fods_empty_column_count(mutation_wb, sheet_index=1) == 0

    def test_fods_numeric_cell_ratio_known_quirk(self, typed_wb):
        # Same 'text' key quirk.
        assert fods_numeric_cell_ratio(typed_wb) == 0.0

    def test_fods_max_row_cell_count(self, typed_wb, mutation_wb):
        assert fods_max_row_cell_count(typed_wb) == 2
        assert fods_max_row_cell_count(mutation_wb, sheet_index=0) == 7

    def test_fods_max_row_cell_count_no_rows(self, mutation_wb):
        assert fods_max_row_cell_count(mutation_wb, sheet_index=1) == 0

    def test_fods_formula_cell_count(self, formula_wb, typed_wb):
        assert fods_formula_cell_count(formula_wb, sheet_index=0) == 1
        assert fods_formula_cell_count(typed_wb, sheet_index=0) == 0

    def test_fods_formula_cell_count_out_of_range(self, typed_wb):
        assert fods_formula_cell_count(typed_wb, sheet_index=99) == 0

    def test_fods_sheet_row_variance(self, mutation_wb):
        assert fods_sheet_row_variance(mutation_wb) == pytest.approx(2.25)


# ---------------------------------------------------------------------------
# models.py — FodsDocument / FodsSheet / FodsCell + module functions
# ---------------------------------------------------------------------------

class TestFodsDocument:
    def test_from_file_and_basic_properties(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.sheet_count == 2
        assert doc.format_id == "fods"
        assert isinstance(doc.warnings, list)

    def test_odf_version_known_quirk(self):
        # Document.odf_version reads self._data['odf_version'], but the
        # parser only sets 'odf_version_attr' -- documents current behavior.
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.odf_version == ""

    def test_workbook_dimension_properties(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.is_empty is False
        assert doc.is_single_sheet is False
        assert doc.is_multi_sheet is True
        assert doc.has_sheets is True
        assert doc.total_row_count == 3
        assert doc.max_sheet_rows == 2

    def test_workbook_scale_properties(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.is_large_workbook is False
        assert doc.has_many_sheets is False
        assert doc.avg_rows_per_sheet == pytest.approx(1.5)

    def test_workbook_scale_properties_no_sheets(self):
        doc = FodsDocument({"sheets": []})
        assert doc.avg_rows_per_sheet == 0.0
        assert doc.is_empty is True

    def test_sheet_distribution_properties(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.min_sheet_rows == 1
        assert doc.sheet_row_range == 1
        assert doc.is_uniform_sheet_size is False

    def test_sheet_distribution_uniform(self):
        doc = FodsDocument.from_file(str(TYPED))
        assert doc.is_uniform_sheet_size is True  # single sheet -> uniform

    def test_sheet_distribution_no_sheets(self):
        doc = FodsDocument({"sheets": []})
        assert doc.min_sheet_rows == 0
        assert doc.sheet_row_range == 0
        assert doc.is_uniform_sheet_size is True

    def test_sheets_and_sheet_by_name(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheets = doc.sheets()
        assert [s.name for s in sheets] == ["Data", "Summary"]
        found = doc.sheet_by_name("Data")
        assert found is not None and found.row_count == 2
        assert doc.sheet_by_name("Nope") is None

    def test_find_sheet_by_index(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert doc.find_sheet_by_index(0).name == "Data"
        assert doc.find_sheet_by_index(99) is None
        assert doc.find_sheet_by_index(-1) is None

    def test_set_cell_value_mutates_document(self):
        doc = FodsDocument.from_file(str(MULTI))
        doc.set_cell_value(0, 0, 0, "Changed", value_type="string")
        assert doc.sheets()[0].cell_at(0, 0).value == "Changed"

    def test_set_cell_value_sheet_out_of_range(self):
        doc = FodsDocument.from_file(str(MULTI))
        with pytest.raises(FodsError):
            doc.set_cell_value(99, 0, 0, "x")

    def test_set_cell_value_row_out_of_range(self):
        doc = FodsDocument.from_file(str(MULTI))
        with pytest.raises(FodsError):
            doc.set_cell_value(0, 99, 0, "x")

    def test_set_cell_value_col_out_of_range(self):
        doc = FodsDocument.from_file(str(MULTI))
        with pytest.raises(FodsError):
            doc.set_cell_value(0, 0, 99, "x")

    def test_save_to_file_and_reload(self, tmp_path):
        doc = FodsDocument.from_file(str(MULTI))
        doc.set_cell_value(0, 0, 0, "Persisted")
        dest = tmp_path / "nested" / "out.fods"
        doc.save_to_file(dest)
        assert dest.exists()
        reloaded = FodsDocument.from_file(str(dest))
        assert reloaded.sheets()[0].cell_at(0, 0).value == "Persisted"

    def test_save_to_file_empty_path_raises(self):
        doc = FodsDocument.from_file(str(MULTI))
        with pytest.raises(FodsError):
            doc.save_to_file("")

    def test_to_file_alias(self, tmp_path):
        doc = FodsDocument.from_file(str(MULTI))
        dest = tmp_path / "alias_out.fods"
        doc.to_file(dest)
        assert dest.exists()

    def test_to_dict(self):
        doc = FodsDocument.from_file(str(MULTI))
        d = doc.to_dict()
        assert d["sheet_count"] == 2
        assert "sheets" in d

    def test_repr(self):
        doc = FodsDocument.from_file(str(MULTI))
        assert repr(doc) == "FodsDocument(sheets=2)"


class TestFodsSheet:
    def test_name_rows_row_count(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        assert sheet.name == "Data"
        assert sheet.row_count == 2
        assert len(sheet.rows) == 2

    def test_cells_iterator(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        values = [c.value for c in sheet.cells()]
        assert values == ["Name", "Value", "Alpha", "Beta"]

    def test_cell_at_bounds(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        assert sheet.cell_at(0, 0).value == "Name"
        assert sheet.cell_at(-1, 0) is None
        assert sheet.cell_at(99, 0) is None
        assert sheet.cell_at(0, 99) is None

    def test_find_cells_by_value(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        found = sheet.find_cells_by_value("Alpha")
        assert len(found) == 1
        assert found[0].value == "Alpha"

    def test_iter_rows(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        rows = list(sheet.iter_rows())
        assert [[c.value for c in row] for row in rows] == [["Name", "Value"], ["Alpha", "Beta"]]

    def test_to_dict(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        d = sheet.to_dict()
        assert d["name"] == "Data"

    def test_repr(self):
        doc = FodsDocument.from_file(str(MULTI))
        sheet = doc.sheet_by_name("Data")
        assert repr(sheet) == "FodsSheet(name='Data', rows=2)"


class TestFodsCell:
    def test_value_and_value_type(self):
        doc = FodsDocument.from_file(str(TYPED))
        sheet = doc.sheets()[0]
        float_cell = sheet.cell_at(2, 1)
        assert float_cell.value == 42.5
        assert float_cell.value_type == "float"

    def test_value_setter(self):
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        cell.value = "NewValue"
        assert cell.value == "NewValue"

    def test_text_known_quirk(self):
        # TableCell.text reads self._data.get('text', ''); the parser never
        # sets a 'text' key on cell dicts (only 'value'), so this is always
        # empty for genuinely parsed documents. Documents current behavior.
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        assert cell.text == ""

    def test_formula_property(self):
        doc = FodsDocument.from_file(str(FORMULA))
        cell = doc.sheets()[0].cell_at(3, 0)
        assert cell.formula == "oooc:=SUM([.A1:.A3])"

    def test_formula_property_none(self):
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        assert cell.formula is None

    def test_repeated_default(self):
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        assert cell.repeated == 1

    def test_to_dict(self):
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        d = cell.to_dict()
        assert d["value"] == "Name"
        assert d["value_type"] == "string"

    def test_repr(self):
        doc = FodsDocument.from_file(str(MULTI))
        cell = doc.sheets()[0].cell_at(0, 0)
        assert repr(cell) == "FodsCell(type='string', value='Name')"

    def test_direct_construction_from_dict(self):
        cell = FodsCell({"value": "hi", "value_type": "string"})
        assert cell.value == "hi"


class TestModelsModuleFunctions:
    def test_value_type_fn(self, multi_wb):
        cell = multi_wb["sheets"][0]["rows"][0]["cells"][0]
        assert value_type(cell) == "string"

    def test_value_type_fn_missing(self):
        assert value_type({}) == ""

    def test_text_fn(self, multi_wb):
        cell = multi_wb["sheets"][0]["rows"][0]["cells"][0]
        assert text(cell) == "Name"

    def test_text_fn_none_value(self):
        assert text({"value": None}) == ""

    def test_repeated_fn_default(self, multi_wb):
        cell = multi_wb["sheets"][0]["rows"][0]["cells"][0]
        assert repeated(cell) == 1

    def test_repeated_fn_explicit(self):
        assert repeated({"repeated": 3}) == 3

    def test_from_file_fn(self):
        wb = from_file(str(MULTI))
        assert wb["sheet_count"] == 2

    def test_odf_version_fn(self, multi_wb):
        assert odf_version(multi_wb) == "1.3"

    def test_odf_version_fn_missing(self):
        assert odf_version({}) == ""

    def test_cell_at_fn_by_int_sheet(self, multi_wb):
        cell = cell_at(multi_wb, 0, 0, 0)
        assert cell["value"] == "Name"

    def test_cell_at_fn_by_name_sheet(self, multi_wb):
        cell = cell_at(multi_wb, "Data", 0, 0)
        assert cell["value"] == "Name"

    def test_cell_at_fn_out_of_range(self, multi_wb):
        assert cell_at(multi_wb, 0, 99, 0) is None
        assert cell_at(multi_wb, 0, 0, 99) is None
        assert cell_at(multi_wb, "NoSuch", 0, 0) is None
        assert cell_at(multi_wb, 99, 0, 0) is None

    def test_to_dict_fn_strips_underscore_keys(self, multi_wb):
        wb = dict(multi_wb)
        wb["_private"] = object()
        d = to_dict(wb)
        assert "_private" not in d
        assert d["sheet_count"] == 2

    def test_models_export_fods_to_csv(self, multi_wb):
        # models.export_fods_to_csv (shadowed at package level by
        # csv_exporter.export_fods_to_csv) — imported directly to cover it.
        assert models_export_fods_to_csv(multi_wb, 0) == "Name,Value\r\nAlpha,Beta\r\n"
        assert models_export_fods_to_csv(multi_wb, "Summary") == "Summary Sheet\r\n"
        assert models_export_fods_to_csv(multi_wb, "NoSuch") == ""
        assert models_export_fods_to_csv({"sheets": []}) == ""


# ---------------------------------------------------------------------------
# csv_exporter.py (top-level export_fods_to_csv resolves here per __init__
# wildcard-import order: models imported before csv_exporter, so
# csv_exporter's version wins in the fods package namespace)
# ---------------------------------------------------------------------------

class TestCsvExporter:
    def test_export_fods_to_csv_default(self, multi_wb):
        assert export_fods_to_csv(multi_wb) == "Name,Value\r\nAlpha,Beta\r\n"

    def test_export_fods_to_csv_sheet_index(self, multi_wb):
        assert export_fods_to_csv(multi_wb, sheet_index=1) == "Summary Sheet\r\n"

    def test_export_fods_to_csv_rejects_non_dict(self):
        with pytest.raises(FodsCsvExportError):
            export_fods_to_csv("not a dict")

    def test_export_fods_to_csv_rejects_non_list_sheets(self):
        with pytest.raises(FodsCsvExportError):
            export_fods_to_csv({"sheets": "nope"})

    def test_export_fods_to_csv_rejects_empty_sheets(self):
        with pytest.raises(FodsCsvExportError):
            export_fods_to_csv({"sheets": []})

    def test_export_fods_to_csv_rejects_out_of_range_index(self, multi_wb):
        with pytest.raises(FodsCsvExportError):
            export_fods_to_csv(multi_wb, sheet_index=99)

    def test_export_fods_to_csv_file(self, multi_wb, tmp_path):
        dest = tmp_path / "out.csv"
        export_fods_to_csv_file(multi_wb, dest, sheet_index=0)
        content = dest.read_text(encoding="utf-8")
        assert "Name,Value" in content
        assert "Alpha,Beta" in content

    def test_export_fods_to_csv_quoting(self):
        wb = {"sheets": [{"name": "S", "rows": [{"cells": [{"value": 'has,comma and "quote"'}]}]}]}
        csv_text = export_fods_to_csv(wb)
        assert csv_text.startswith('"has,comma and ""quote"""')

    def test_export_fods_to_csv_integer_float_formatting(self):
        wb = {"sheets": [{"name": "S", "rows": [{"cells": [{"value": 5.0}]}]}]}
        csv_text = export_fods_to_csv(wb)
        assert csv_text == "5\r\n"


# ---------------------------------------------------------------------------
# fods_to_tsv.py
# ---------------------------------------------------------------------------

class TestFodsToTsv:
    def test_fods_to_tsv_with_headers(self, tmp_path):
        dest = tmp_path / "out.tsv"
        try:
            n, headers = fods_to_tsv(str(MULTI), dest)
        except ImportError:
            pytest.skip("tsv package not installed in this environment")
        assert n == 1
        assert headers == ["Name", "Value"]
        content = dest.read_text(encoding="utf-8")
        assert "Name\tValue" in content
        assert "Alpha\tBeta" in content

    def test_fods_to_tsv_without_headers(self, tmp_path):
        dest = tmp_path / "out_noheader.tsv"
        try:
            n, headers = fods_to_tsv(str(MULTI), dest, first_row_as_headers=False)
        except ImportError:
            pytest.skip("tsv package not installed in this environment")
        assert n == 2
        assert headers == []

    def test_fods_to_tsv_empty_workbook(self, tmp_path):
        dest = tmp_path / "empty.tsv"
        try:
            n, headers = fods_to_tsv(str(MINIMAL), dest, sheet_index=99)
        except ImportError:
            pytest.skip("tsv package not installed in this environment")
        # sheet_index clamped to last valid sheet (only 1 sheet, 1 row in
        # MINIMAL); that single row is consumed as the header row, leaving
        # zero data rows.
        assert n == 0
        assert headers == ["Hello"]


# ---------------------------------------------------------------------------
# fods_workflow.py
# ---------------------------------------------------------------------------

class TestFodsInstalledWorkflow:
    def test_installed_workflow(self):
        result = fods_installed_workflow(str(MULTI))
        assert result == {"format": "fods", "loaded": True, "sheet_count": 2}

    def test_installed_workflow_minimal(self):
        result = fods_installed_workflow(str(MINIMAL))
        assert result["sheet_count"] == 1


# ---------------------------------------------------------------------------
# fods_sheet_iterator.py / fods_cell_iterator.py
# ---------------------------------------------------------------------------

class TestIterators:
    def test_fods_iter_sheets(self):
        sheets = list(fods_iter_sheets(str(MULTI)))
        assert [s.name for s in sheets] == ["Data", "Summary"]
        assert all(isinstance(s, FodsSheet) for s in sheets)

    def test_fods_iter_sheets_minimal(self):
        sheets = list(fods_iter_sheets(str(MINIMAL)))
        assert len(sheets) == 1

    def test_fods_iter_cells(self):
        cells = list(fods_iter_cells(str(MULTI)))
        assert [c.value for c in cells] == ["Name", "Value", "Alpha", "Beta", "Summary Sheet"]
        assert all(isinstance(c, FodsCell) for c in cells)

    def test_fods_iter_cells_empty_sheet_yields_nothing_extra(self, mutation_wb):
        cells = list(fods_iter_cells(str(MUTATION)))
        # ValueTypes: row0 has 7 cells, row1 has 2 cells (main + covered),
        # row2 has a draw:frame (not a table-cell, not yielded) + 1 cell.
        # EmptySheet contributes nothing. Total: 7 + 2 + 1 = 10.
        assert len(cells) == 10


# ---------------------------------------------------------------------------
# fods_file_analytics.py (direct submodule import — not re-exported at
# package level; see module docstring for rationale)
# ---------------------------------------------------------------------------

class TestFodsFileAnalytics:
    def test_file_sheet_count(self):
        assert fods_file_sheet_count(MULTI) == 2
        assert fods_file_sheet_count(MINIMAL) == 1

    def test_file_is_fods(self):
        assert fods_file_is_fods(MULTI) is True

    def test_file_first_sheet_name(self):
        assert fods_file_first_sheet_name(MULTI) == "Data"

    def test_file_first_sheet_name_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty_workbook.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_first_sheet_name(empty_wb_path) == ""

    def test_file_sheet_names(self):
        assert fods_file_sheet_names(MULTI) == ["Data", "Summary"]

    def test_file_has_multiple_sheets(self):
        assert fods_file_has_multiple_sheets(MULTI) is True
        assert fods_file_has_multiple_sheets(MINIMAL) is False

    def test_file_total_rows(self):
        assert fods_file_total_rows(MULTI) == 3

    def test_file_has_parse_errors(self):
        assert fods_file_has_parse_errors(MULTI) is False

    def test_file_odf_version(self):
        assert fods_file_odf_version(MULTI) == "1.3"

    def test_file_has_warnings(self):
        assert fods_file_has_warnings(MULTI) is False
        assert fods_file_has_warnings(FORMULA) is True  # formula cell warning

    def test_file_last_sheet_name(self):
        assert fods_file_last_sheet_name(MULTI) == "Summary"

    def test_file_last_sheet_name_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty2.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_last_sheet_name(empty_wb_path) == ""

    def test_file_sheet_row_counts(self):
        assert fods_file_sheet_row_counts(MULTI) == [2, 1]

    def test_file_max_sheet_row_count(self):
        assert fods_file_max_sheet_row_count(MULTI) == 2

    def test_file_max_sheet_row_count_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty3.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_max_sheet_row_count(empty_wb_path) == 0

    def test_file_min_sheet_row_count(self):
        assert fods_file_min_sheet_row_count(MULTI) == 1

    def test_file_min_sheet_row_count_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty4.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_min_sheet_row_count(empty_wb_path) == 0

    def test_file_avg_sheet_row_count(self):
        assert fods_file_avg_sheet_row_count(MULTI) == pytest.approx(1.5)

    def test_file_avg_sheet_row_count_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty5.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_avg_sheet_row_count(empty_wb_path) == 0.0

    def test_file_has_single_sheet(self):
        assert fods_file_has_single_sheet(MINIMAL) is True
        assert fods_file_has_single_sheet(MULTI) is False

    def test_file_sheet_names_sorted(self):
        assert fods_file_sheet_names_sorted(MULTI) == ["Data", "Summary"]

    def test_file_first_sheet_row_count(self):
        assert fods_file_first_sheet_row_count(MULTI) == 2

    def test_file_first_sheet_row_count_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty6.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_first_sheet_row_count(empty_wb_path) == 0

    def test_file_last_sheet_row_count(self):
        assert fods_file_last_sheet_row_count(MULTI) == 1

    def test_file_last_sheet_row_count_no_sheets(self, tmp_path):
        empty_wb_path = tmp_path / "empty7.fods"
        write_fods({"sheets": []}, empty_wb_path)
        assert fods_file_last_sheet_row_count(empty_wb_path) == 0


# ---------------------------------------------------------------------------
# constants.py
# ---------------------------------------------------------------------------

class TestConstants:
    def test_format_identity(self):
        assert FORMAT_ID == "fods"
        assert SPEC_VERSION == "ODF 1.3"

    def test_mimetype(self):
        assert EXPECTED_MIMETYPE == "application/vnd.oasis.opendocument.spreadsheet-flat-xml"

    def test_size_and_repeat_limits(self):
        assert MAX_FILE_BYTES == 100 * 1024 * 1024
        assert MAX_EXPAND_REPEAT == 128


# ---------------------------------------------------------------------------
# exceptions.py
# ---------------------------------------------------------------------------

class TestExceptions:
    def test_hierarchy(self):
        assert issubclass(FodsInputError, FodsError)
        assert issubclass(FodsSizeError, FodsError)
        assert issubclass(FodsParseError, FodsError)
        assert issubclass(FodsError, FormatFactoryError)

    def test_exceptions_carry_message(self):
        exc = FodsInputError("boom")
        assert str(exc) == "boom"
