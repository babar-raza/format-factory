"""Gnumeric gap-ledger coverage — explicit tests for every gap-listed capability.

Consolidated coverage file for the 45 GNUMERIC missing_test_coverage gaps
(reports/capability-layer/gap-ledger.json, gap_id prefix GAP-Gnumeric-FOSS-*),
plus the core codec surface (load, write_gnumeric, create_gnumeric, probe_gnumeric,
gnumeric_installed_workflow) and every function exported from gnumeric_analytics.py
and gnumeric_sheet_analytics.py.

Targets (gap-ledger capability names -> implementation):
    Installed Workflow / Gnumeric Installed Workflow -> gnumeric_installed_workflow
    Gnumeric Column Count File           -> gnumeric_column_count_file
    Gnumeric Cell Count File             -> gnumeric_cell_count_file
    Gnumeric Empty Cell Count            -> gnumeric_empty_cell_count
    Gnumeric Nonempty Cell Count File    -> gnumeric_nonempty_cell_count_file
    Gnumeric Total Cell Count            -> gnumeric_total_cell_count
    Gnumeric Sheet Count                 -> gnumeric_sheet_count
    Gnumeric Has Multiple Sheets         -> gnumeric_has_multiple_sheets
    Gnumeric Average Cells Per Sheet     -> gnumeric_average_cells_per_sheet
    Gnumeric Numeric Density             -> gnumeric_numeric_density
    Gnumeric String Density              -> gnumeric_string_density
    Gnumeric Max Cell Length             -> gnumeric_max_cell_length
    Gnumeric Min Cell Length             -> gnumeric_min_cell_length
    Gnumeric All Sheets Have Data        -> gnumeric_all_sheets_have_data
    Gnumeric Is Single Sheet             -> gnumeric_is_single_sheet
    Gnumeric Data Density                -> gnumeric_data_density
    Gnumeric Avg Row Count               -> gnumeric_avg_row_count
    Gnumeric Row Count Variance          -> gnumeric_row_count_variance
    Gnumeric Longest Row Index           -> gnumeric_longest_row_index
    Gnumeric Distinct String Count       -> gnumeric_distinct_string_count
    Probe Gnumeric Codec                 -> probe_gnumeric_codec
    Gnumeric First Sheet Name            -> gnumeric_first_sheet_name
    Gnumeric Unique Value Count          -> gnumeric_unique_value_count
    Gnumeric Last Sheet Name             -> gnumeric_last_sheet_name
    Gnumeric Iter Sheets                 -> gnumeric_iter_sheets
    Gnumeric To Abw                      -> gnumeric_to_abw
    Correlation Columns                  -> correlation_columns
    Workbook Sheet Count                 -> workbook_sheet_count
    Workbook Total Cell Count            -> workbook_total_cell_count
    Workbook Has Data                    -> workbook_has_data
    Workbook Is Gnumeric                 -> workbook_is_gnumeric
    Workbook Max Sheet Cell Count        -> workbook_max_sheet_cell_count
    Is Large Workbook                    -> GnumericDocument.is_large_workbook
    Has Many Sheets                      -> GnumericDocument.has_many_sheets
    Is Cell Dense                        -> GnumericDocument.is_cell_dense
    Max Cells Per Sheet                  -> GnumericDocument.max_cells_per_sheet
    Min Cells Per Sheet                  -> GnumericDocument.min_cells_per_sheet
    Cell Count Range                     -> GnumericDocument.cell_count_range
    Has Uniform Cell Distribution        -> GnumericDocument.has_uniform_cell_distribution
    Sheet Cell Variance                  -> GnumericDocument.sheet_cell_variance
    Has Large Sheets                     -> GnumericDocument.has_large_sheets
    Save To File                         -> GnumericDocument.save_to_file
    Gnumericerror                        -> GnumericError
    Gnumericparseerror                   -> GnumericParseError

Also covers (explicitly named by the task): load, write_gnumeric, roundtrip
(load + write_gnumeric identity — the gnumeric package has no standalone
`roundtrip()` function), probe_gnumeric, gnumeric_installed_workflow,
GnumericWriteError, and every exported analytics/workbook-stats/codec function.
"""
from __future__ import annotations

import gzip
import inspect
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import gnumeric
from gnumeric import (
    GnumericDocument,
    add_sheet,
    average_column,
    average_row,
    clear_cell,
    clear_sheet,
    copy_sheet,
    correlation_columns,
    count_nonempty_cells,
    create_gnumeric,
    delete_sheet,
    export_to_csv,
    export_to_json,
    extract_values,
    fill_column,
    fill_row,
    get_all_values,
    get_cell_count,
    get_cell_value,
    get_column,
    get_column_count,
    get_column_values,
    get_row,
    get_row_count,
    get_row_values,
    get_sheet_as_rows,
    get_sheet_by_name,
    get_sheet_count,
    get_sheet_index,
    get_sheet_metadata,
    get_sheet_names,
    gnumeric_installed_workflow,
    gnumeric_iter_sheets,
    load,
    max_column_value,
    min_column_value,
    probe_gnumeric,
    probe_gnumeric_codec,
    read_cell,
    rename_sheet,
    row_count,
    set_cell_value,
    sheet_names,
    sum_column,
    sum_row,
    workbook_has_data,
    workbook_is_gnumeric,
    workbook_max_sheet_cell_count,
    workbook_sheet_count,
    workbook_sheet_names,
    workbook_total_cell_count,
    write_gnumeric,
)
from gnumeric import gnumeric_analytics as _ga
from gnumeric import gnumeric_sheet_analytics as _gsa
from gnumeric.exceptions import GnumericError as ExcGnumericError
from gnumeric.exceptions import GnumericParseError as ExcGnumericParseError
from gnumeric.exceptions import GnumericWriteError as ExcGnumericWriteError
from gnumeric.gnumeric_codec import GnumericError as CodecGnumericError
from gnumeric.gnumeric_codec import GnumericParseError as CodecGnumericParseError
from gnumeric.gnumeric_to_abw import gnumeric_to_abw
from gnumeric.spec.workbook.sheet import Sheet

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"
MULTI = SAMPLES / "multi-cell-basic.gnumeric"
EMPTY = SAMPLES / "empty-sheet.gnumeric"


# ---------------------------------------------------------------------------
# probe_gnumeric / probe_gnumeric_codec
# ---------------------------------------------------------------------------


class TestProbeGnumeric:
    def test_probe_valid_minimal(self):
        assert probe_gnumeric(MINIMAL) is True

    def test_probe_valid_multi(self):
        assert probe_gnumeric(MULTI) is True

    def test_probe_invalid_bytes(self):
        assert probe_gnumeric(b"not gzip data") is False

    def test_probe_missing_file(self):
        assert probe_gnumeric("/no/such/file.gnumeric") is False

    def test_probe_bytes_source(self):
        data = MULTI.read_bytes()
        assert probe_gnumeric(data) is True

    def test_probe_gzip_but_wrong_namespace(self):
        payload = gzip.compress(b"<not-gnumeric-xml/>")
        assert probe_gnumeric(payload) is False


class TestProbeGnumericCodec:
    def test_returns_dict_for_valid_file(self):
        result = probe_gnumeric_codec(MULTI)
        assert result["format"] == "gnumeric"
        assert result["valid"] is True
        assert result["file_size"] > 0

    def test_returns_error_dict_for_missing_file(self):
        result = probe_gnumeric_codec("/no/such/file.gnumeric")
        assert result["format"] == "gnumeric"
        assert result["valid"] is False
        assert "error" in result

    def test_returns_error_dict_for_bytes_input(self):
        result = probe_gnumeric_codec(b"abc")
        assert result["valid"] is False
        assert "error" in result


# ---------------------------------------------------------------------------
# load / roundtrip
# ---------------------------------------------------------------------------


class TestLoadGnumeric:
    def test_load_returns_model_dict(self):
        model = load(MINIMAL)
        assert isinstance(model, dict)
        assert model["is_gnumeric"] is True
        assert model["sheet_count"] == 1

    def test_load_multi_cell_counts(self):
        model = load(MULTI)
        assert model["sheet_count"] == 1
        assert model["cell_count"] == 4

    def test_load_empty_sheet(self):
        model = load(EMPTY)
        assert model["sheet_count"] == 1
        assert model["cell_count"] == 0

    def test_load_from_bytes(self):
        data = MULTI.read_bytes()
        model = load(data)
        assert model["cell_count"] == 4

    def test_load_missing_file_raises(self):
        with pytest.raises(CodecGnumericParseError):
            load("/no/such/file.gnumeric")

    def test_load_garbage_bytes_raises(self):
        with pytest.raises(CodecGnumericParseError):
            load(b"not a gnumeric file at all")

    def test_load_all_corpus_samples(self):
        for path in sorted(SAMPLES.glob("*.gnumeric")):
            model = load(path)
            assert model["is_gnumeric"] is True, f"{path.name} not Gnumeric"
            assert "sheets" in model


class TestCreateAndWriteGnumeric:
    """Covers: create_gnumeric, write_gnumeric, and the load/write roundtrip.

    The gnumeric package has no standalone ``roundtrip()`` function — the
    load() + write_gnumeric() pair is the roundtrip contract, verified below.
    """

    def test_create_gnumeric_basic(self):
        model = create_gnumeric([{"name": "Data", "rows": [["a", "b"], ["1", "2"]]}])
        assert model["is_gnumeric"] is True
        assert model["sheet_count"] == 1
        assert model["cell_count"] == 4

    def test_create_gnumeric_default_sheet_names(self):
        model = create_gnumeric([{"rows": [["x"]]}, {"rows": [["y"]]}])
        names = [s["name"] for s in model["sheets"]]
        assert names == ["Sheet1", "Sheet2"]

    def test_create_gnumeric_empty_list(self):
        model = create_gnumeric([])
        assert model["sheet_count"] == 0
        assert model["cell_count"] == 0

    def test_write_gnumeric_then_load_roundtrip(self):
        model = create_gnumeric(
            [{"name": "Data", "rows": [["x", "y"], ["1", "2"], ["2", "4"], ["3", "6"]]}]
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.gnumeric"
            write_gnumeric(model, dest)
            assert dest.exists()
            assert dest.stat().st_size > 0
            reloaded = load(dest)
            assert reloaded["sheet_count"] == 1
            assert reloaded["cell_count"] == 8
            assert reloaded["sheets"][0]["name"] == "Data"

    def test_roundtrip_preserves_cell_values(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "roundtrip.gnumeric"
            write_gnumeric(load(MULTI), dest)
            reloaded = load(dest)
            assert sorted(reloaded["sheets"][0]["cell_values"]) == sorted(
                ["Name", "Score", "Alice", "42"]
            )

    def test_write_gnumeric_invalid_model_raises(self):
        with pytest.raises(CodecGnumericError):
            write_gnumeric({"is_gnumeric": False}, "unused.gnumeric")

    def test_write_gnumeric_non_dict_model_raises(self):
        with pytest.raises(CodecGnumericError):
            write_gnumeric("not a model", "unused.gnumeric")

    def test_write_gnumeric_output_is_gzip(self):
        model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.gnumeric"
            write_gnumeric(model, dest)
            assert dest.read_bytes()[:2] == b"\x1f\x8b"


# ---------------------------------------------------------------------------
# Sheet / cell metadata accessors
# ---------------------------------------------------------------------------


class TestSheetMetadataAccessors:
    def test_get_sheet_count(self):
        assert get_sheet_count(MULTI) == 1

    def test_get_cell_count(self):
        assert get_cell_count(MULTI) == 4

    def test_extract_values(self):
        values = extract_values(MULTI)
        assert sorted(values) == sorted(["Name", "Score", "Alice", "42"])

    def test_extract_values_empty_sheet(self):
        assert extract_values(EMPTY) == []

    def test_get_sheet_metadata(self):
        meta = get_sheet_metadata(MULTI)
        assert len(meta) == 1
        assert meta[0]["name"] == "Sheet1"
        assert meta[0]["cell_count"] == 4

    def test_get_sheet_names(self):
        assert get_sheet_names(MULTI) == ["Sheet1"]

    def test_get_sheet_names_empty_source(self):
        assert get_sheet_names(EMPTY) == ["Empty"]


class TestCellAccessors:
    def test_get_cell_value(self):
        model = load(MULTI)
        assert get_cell_value(model, 0, 0, 0) == "Name"
        assert get_cell_value(model, 0, 1, 1) == "42"

    def test_get_cell_value_missing_cell_returns_empty(self):
        model = load(MULTI)
        assert get_cell_value(model, 0, 9, 9) == ""

    def test_get_cell_value_bad_sheet_idx_raises(self):
        model = load(MULTI)
        with pytest.raises(CodecGnumericError):
            get_cell_value(model, 5, 0, 0)

    def test_get_cell_value_non_dict_model_raises(self):
        with pytest.raises(TypeError):
            get_cell_value("not a dict", 0, 0, 0)

    def test_set_cell_value_is_immutable(self):
        model = load(MULTI)
        updated = set_cell_value(model, 0, 0, 0, "Changed")
        assert get_cell_value(updated, 0, 0, 0) == "Changed"
        assert get_cell_value(model, 0, 0, 0) == "Name"

    def test_set_cell_value_updates_cell_count(self):
        model = load(EMPTY)
        updated = set_cell_value(model, 0, 0, 0, "X")
        assert updated["cell_count"] == 1

    def test_set_cell_value_bad_type_raises(self):
        model = load(MULTI)
        with pytest.raises(TypeError):
            set_cell_value(model, 0, 0, 0, 123)

    def test_get_row(self):
        model = load(MULTI)
        assert get_row(model, 0, 0) == ["Name", "Score"]
        assert get_row(model, 0, 1) == ["Alice", "42"]

    def test_get_row_missing_returns_empty(self):
        model = load(MULTI)
        assert get_row(model, 0, 9) == []

    def test_get_column(self):
        model = load(MULTI)
        assert get_column(model, 0, 0) == ["Name", "Alice"]
        assert get_column(model, 0, 1) == ["Score", "42"]

    def test_read_cell_present(self):
        model = load(MULTI)
        assert read_cell(model, 0, 0, 0) == "Name"

    def test_read_cell_missing_returns_none(self):
        model = load(MULTI)
        assert read_cell(model, 0, 9, 9) is None

    def test_clear_cell(self):
        model = load(MULTI)
        cleared = clear_cell(model, 0, 0, 0)
        assert read_cell(cleared, 0, 0, 0) is None
        assert read_cell(model, 0, 0, 0) == "Name"
        assert cleared["cell_count"] == 3


# ---------------------------------------------------------------------------
# Sheet mutation operations
# ---------------------------------------------------------------------------


class TestSheetMutationOps:
    def test_add_sheet_appends(self):
        model = load(MULTI)
        updated = add_sheet(model, "Second")
        assert updated["sheet_count"] == 2
        assert [s["name"] for s in updated["sheets"]] == ["Sheet1", "Second"]

    def test_add_sheet_auto_name(self):
        model = load(MULTI)
        updated = add_sheet(model, "")
        assert updated["sheets"][-1]["name"] == "Sheet2"

    def test_add_sheet_insert_at(self):
        model = load(MULTI)
        updated = add_sheet(model, "First", insert_at=0)
        assert [s["name"] for s in updated["sheets"]] == ["First", "Sheet1"]

    def test_delete_sheet(self):
        model = add_sheet(load(MULTI), "Second")
        updated = delete_sheet(model, 0)
        assert updated["sheet_count"] == 1
        assert updated["sheets"][0]["name"] == "Second"

    def test_delete_sheet_out_of_range_raises(self):
        model = load(MULTI)
        with pytest.raises(CodecGnumericError):
            delete_sheet(model, 5)

    def test_rename_sheet(self):
        model = load(MULTI)
        updated = rename_sheet(model, 0, "Renamed")
        assert updated["sheets"][0]["name"] == "Renamed"

    def test_rename_sheet_bad_type_raises(self):
        model = load(MULTI)
        with pytest.raises(TypeError):
            rename_sheet(model, 0, 123)

    def test_get_sheet_by_name_found(self):
        model = load(MULTI)
        sheet = get_sheet_by_name(model, "Sheet1")
        assert sheet is not None
        assert sheet["cell_count"] == 4

    def test_get_sheet_by_name_not_found(self):
        model = load(MULTI)
        assert get_sheet_by_name(model, "NoSuchSheet") is None

    def test_copy_sheet(self):
        model = load(MULTI)
        updated = copy_sheet(model, 0)
        assert updated["sheet_count"] == 2
        assert updated["sheets"][1]["name"] == "Sheet1 (Copy)"
        assert updated["sheets"][1]["cell_grid"] == updated["sheets"][0]["cell_grid"]

    def test_copy_sheet_out_of_range_raises(self):
        model = load(MULTI)
        with pytest.raises(CodecGnumericError):
            copy_sheet(model, 5)

    def test_get_sheet_index_found(self):
        model = load(MULTI)
        assert get_sheet_index(model, "Sheet1") == 0

    def test_get_sheet_index_not_found_raises(self):
        model = load(MULTI)
        with pytest.raises(KeyError):
            get_sheet_index(model, "Missing")


# ---------------------------------------------------------------------------
# Export formats
# ---------------------------------------------------------------------------


class TestExportFormats:
    def test_export_to_csv(self):
        csv_str = export_to_csv(MULTI)
        assert csv_str == "Name,Score\r\nAlice,42\r\n"

    def test_export_to_csv_custom_delimiter(self):
        csv_str = export_to_csv(MULTI, delimiter=";")
        assert csv_str == "Name;Score\r\nAlice;42\r\n"

    def test_export_to_csv_empty_sheet(self):
        assert export_to_csv(EMPTY) == ""

    def test_export_to_csv_out_of_range_raises(self):
        with pytest.raises(CodecGnumericError):
            export_to_csv(MULTI, sheet_index=5)

    def test_export_to_json(self):
        json_str = export_to_json(MULTI)
        assert '"name": "Sheet1"' in json_str
        assert '"Name"' in json_str
        assert '"42"' in json_str

    def test_export_to_json_empty_sheet(self):
        json_str = export_to_json(EMPTY)
        assert '"name": "Empty"' in json_str
        assert '"rows": []' in json_str


# ---------------------------------------------------------------------------
# gnumeric_installed_workflow
# ---------------------------------------------------------------------------


class TestGnumericInstalledWorkflow:
    def test_returns_expected_dict(self):
        result = gnumeric_installed_workflow(MULTI)
        assert result == {
            "format": "gnumeric",
            "loaded": True,
            "sheet_count": 1,
            "cell_count": 4,
        }

    def test_empty_sheet_workflow(self):
        result = gnumeric_installed_workflow(EMPTY)
        assert result["loaded"] is True
        assert result["sheet_count"] == 1
        assert result["cell_count"] == 0

    def test_accepts_bytes_source(self):
        result = gnumeric_installed_workflow(MULTI.read_bytes())
        assert result["cell_count"] == 4


# ---------------------------------------------------------------------------
# Workbook stats (gnumeric_workbook_stats.py)
# ---------------------------------------------------------------------------


class TestWorkbookStats:
    def test_sum_column(self):
        model = load(MULTI)
        assert sum_column(model, 0, 1) == 42.0

    def test_sum_column_out_of_range_returns_zero(self):
        model = load(MULTI)
        assert sum_column(model, 5, 0) == 0.0

    def test_sum_row(self):
        model = load(MULTI)
        assert sum_row(model, 0, 1) == 42.0

    def test_fill_column(self):
        model = load(EMPTY)
        updated = fill_column(model, 0, 0, ["10", "20", "30"])
        assert get_column(updated, 0, 0) == ["10", "20", "30"]

    def test_fill_row(self):
        model = load(EMPTY)
        updated = fill_row(model, 0, 0, ["a", "b", "c"])
        assert get_row(updated, 0, 0) == ["a", "b", "c"]

    def test_get_all_values(self):
        model = load(MULTI)
        assert sorted(get_all_values(model, 0)) == sorted(["Name", "Score", "Alice", "42"])

    def test_get_all_values_out_of_range(self):
        model = load(MULTI)
        assert get_all_values(model, 5) == []

    def test_clear_sheet(self):
        model = load(MULTI)
        cleared = clear_sheet(model, 0)
        assert cleared["sheets"][0]["cell_count"] == 0
        assert cleared["cell_count"] == 0
        assert model["cell_count"] == 4

    def test_get_sheet_as_rows(self):
        model = load(MULTI)
        assert get_sheet_as_rows(model, 0) == [["Name", "Score"], ["Alice", "42"]]

    def test_get_sheet_as_rows_empty(self):
        model = load(EMPTY)
        assert get_sheet_as_rows(model, 0) == []

    def test_sheet_names(self):
        model = load(MULTI)
        assert sheet_names(model) == ["Sheet1"]

    def test_row_count(self):
        model = load(MULTI)
        assert row_count(model, 0) == 2

    def test_row_count_empty_sheet(self):
        model = load(EMPTY)
        assert row_count(model, 0) == 0

    def test_get_row_values(self):
        model = load(MULTI)
        assert get_row_values(model, 0, 0) == ["Name", "Score"]

    def test_get_row_values_out_of_range_raises(self):
        model = load(MULTI)
        with pytest.raises(IndexError):
            get_row_values(model, 5, 0)

    def test_get_column_values(self):
        model = load(MULTI)
        assert get_column_values(model, 0, 1) == ["Score", "42"]

    def test_get_column_values_out_of_range_raises(self):
        model = load(MULTI)
        with pytest.raises(IndexError):
            get_column_values(model, 5, 0)

    def test_min_column_value(self):
        model = load(MULTI)
        assert min_column_value(model, 0, 1) == 42.0

    def test_min_column_value_no_numeric_returns_none(self):
        model = load(MULTI)
        assert min_column_value(model, 0, 0) is None

    def test_max_column_value(self):
        model = load(MULTI)
        assert max_column_value(model, 0, 1) == 42.0

    def test_average_column(self):
        model = load(MULTI)
        assert average_column(model, 0, 1) == 42.0

    def test_average_column_no_numeric_returns_zero(self):
        model = load(MULTI)
        assert average_column(model, 0, 0) == 0.0

    def test_average_row(self):
        model = load(MULTI)
        assert average_row(model, 0, 1) == 42.0

    def test_correlation_columns_perfect_positive(self):
        model = create_gnumeric(
            [{"name": "Data", "rows": [["1", "2"], ["2", "4"], ["3", "6"]]}]
        )
        r = correlation_columns(model, 0, 0, 1)
        assert r == pytest.approx(1.0, abs=1e-9)

    def test_correlation_columns_insufficient_data(self):
        model = load(MULTI)
        assert correlation_columns(model, 0, 0, 1) == 0.0

    def test_get_row_count(self):
        model = load(MULTI)
        assert get_row_count(model, 0) == 2

    def test_get_row_count_bad_sheet_raises(self):
        model = load(MULTI)
        with pytest.raises(CodecGnumericError):
            get_row_count(model, 5)

    def test_get_column_count(self):
        model = load(MULTI)
        assert get_column_count(model, 0) == 2

    def test_count_nonempty_cells(self):
        model = load(MULTI)
        assert count_nonempty_cells(model, 0) == 4

    def test_workbook_sheet_count(self):
        model = load(MULTI)
        assert workbook_sheet_count(model) == 1

    def test_workbook_sheet_count_non_dict(self):
        assert workbook_sheet_count("not a dict") == 0

    def test_workbook_total_cell_count(self):
        model = load(MULTI)
        assert workbook_total_cell_count(model) == 4

    def test_workbook_sheet_names(self):
        model = load(MULTI)
        assert workbook_sheet_names(model) == ["Sheet1"]

    def test_workbook_has_data(self):
        model = load(MULTI)
        assert workbook_has_data(model) is True
        assert workbook_has_data(load(EMPTY)) is False

    def test_workbook_is_gnumeric(self):
        model = load(MULTI)
        assert workbook_is_gnumeric(model) is True

    def test_workbook_max_sheet_cell_count(self):
        model = load(MULTI)
        assert workbook_max_sheet_cell_count(model) == 4


# ---------------------------------------------------------------------------
# gnumeric_analytics.py — model+sheet_idx based functions
# ---------------------------------------------------------------------------


class TestGnumericAnalyticsModelBased:
    """Functions in gnumeric_analytics.py that take (model, sheet_idx)."""

    def test_gnumeric_column_count(self):
        model = load(MULTI)
        assert _ga.gnumeric_column_count(model, 0) == 2

    def test_gnumeric_column_count_out_of_range(self):
        model = load(MULTI)
        assert _ga.gnumeric_column_count(model, 5) == 0

    def test_gnumeric_empty_cell_count(self):
        model = load(MULTI)
        assert _ga.gnumeric_empty_cell_count(model, 0) == 0

    def test_gnumeric_numeric_cell_count(self):
        model = load(MULTI)
        assert _ga.gnumeric_numeric_cell_count(model, 0) == 1

    def test_gnumeric_string_cell_count(self):
        model = load(MULTI)
        assert _ga.gnumeric_string_cell_count(model, 0) == 3

    def test_gnumeric_sheet_summary(self):
        model = load(MULTI)
        assert _ga.gnumeric_sheet_summary(model, 0) == {
            "row_count": 2,
            "col_count": 2,
            "nonempty_cells": 4,
        }

    def test_gnumeric_sheet_summary_empty(self):
        model = load(EMPTY)
        assert _ga.gnumeric_sheet_summary(model, 0) == {
            "row_count": 0,
            "col_count": 0,
            "nonempty_cells": 0,
        }


# ---------------------------------------------------------------------------
# gnumeric_analytics.py — file-path (single-arg) functions
# ---------------------------------------------------------------------------

# Ground truth computed directly from multi-cell-basic.gnumeric
# (Sheet1: (0,0)="Name" (0,1)="Score" (1,0)="Alice" (1,1)="42").
ANALYTICS_MODEL_BASED = frozenset(
    {
        "gnumeric_column_count",
        "gnumeric_empty_cell_count",
        "gnumeric_numeric_cell_count",
        "gnumeric_string_cell_count",
        "gnumeric_sheet_summary",
    }
)

ANALYTICS_EXPECTED_MULTI = {
    "gnumeric_all_sheets_have_data": True,
    "gnumeric_average_cells_per_sheet": 4.0,
    "gnumeric_avg_cell_length": 4.0,
    "gnumeric_avg_column_count": 2.0,
    "gnumeric_avg_numeric_value": 42.0,
    "gnumeric_avg_row_count": 0.0,
    "gnumeric_cell_count_all_sheets": 4,
    "gnumeric_cell_count_file": 4,
    "gnumeric_cell_count_variance": 0.0,
    "gnumeric_cell_to_row_ratio": 2.0,
    "gnumeric_column_count_file": 2,
    "gnumeric_column_variance": 0.0,
    "gnumeric_data_density": 1.0,
    "gnumeric_distinct_string_count": 3,
    "gnumeric_empty_column_count": 0,
    "gnumeric_empty_sheet_count": 0,
    "gnumeric_has_any_string_cell": True,
    "gnumeric_has_empty_cells": False,
    "gnumeric_has_empty_sheets": False,
    "gnumeric_has_multiple_sheets": False,
    "gnumeric_is_all_numeric": False,
    "gnumeric_is_empty": False,
    "gnumeric_is_multi_sheet": False,
    "gnumeric_is_rectangular": True,
    "gnumeric_is_single_sheet": True,
    "gnumeric_longest_row_index": 0,
    "gnumeric_max_cell_length": 5,
    "gnumeric_max_cell_value_length": 5,
    "gnumeric_max_column_count": 2,
    "gnumeric_max_row_count": 0,
    "gnumeric_max_row_length": 2,
    "gnumeric_max_string_cell_length": 5,
    "gnumeric_min_cell_length": 2,
    "gnumeric_min_column_count": 2,
    "gnumeric_min_row_count": 0,
    "gnumeric_nonempty_cell_count_file": 4,
    "gnumeric_nonempty_cell_ratio": 1.0,
    "gnumeric_nonempty_density": 1.0,
    "gnumeric_nonempty_row_count": 2,
    "gnumeric_nonempty_row_ratio": 1.0,
    "gnumeric_numeric_density": 0.25,
    "gnumeric_numeric_range": 0.0,
    "gnumeric_numeric_sum_all": 42.0,
    "gnumeric_numeric_to_string_ratio": 0.0,
    "gnumeric_row_col_ratio": 1.0,
    "gnumeric_row_count_file": 2,
    "gnumeric_row_count_variance": 0.0,
    "gnumeric_row_density_avg": 1.0,
    "gnumeric_sheet_count": 1,
    "gnumeric_sheet_name_lengths": [6],
    "gnumeric_string_density": 0.75,
    "gnumeric_string_ratio": 0.75,
    "gnumeric_total_cell_count": 4,
    "gnumeric_total_row_count": 2,
    "gnumeric_total_string_length": 16,
}


class TestGnumericAnalyticsFileBased:
    @pytest.mark.parametrize(
        "func_name,expected", sorted(ANALYTICS_EXPECTED_MULTI.items())
    )
    def test_analytics_function_on_multi_sample(self, func_name, expected):
        fn = getattr(_ga, func_name)
        result = fn(MULTI)
        if isinstance(expected, float):
            assert result == pytest.approx(expected)
        else:
            assert result == expected

    def test_all_single_arg_analytics_functions_are_covered(self):
        """Guards against new gnumeric_analytics.py functions shipping untested."""
        discovered = {
            name
            for name, _ in inspect.getmembers(_ga, inspect.isfunction)
            if name.startswith("gnumeric_")
        }
        single_arg = discovered - ANALYTICS_MODEL_BASED
        missing = single_arg - set(ANALYTICS_EXPECTED_MULTI)
        assert not missing, f"Uncovered gnumeric_analytics functions: {sorted(missing)}"

    def test_gnumeric_is_empty_on_empty_sheet(self):
        assert _ga.gnumeric_is_empty(EMPTY) is True

    def test_gnumeric_data_density_on_empty_sheet(self):
        assert _ga.gnumeric_data_density(EMPTY) == 0.0

    def test_gnumeric_empty_sheet_count_on_empty_sheet(self):
        assert _ga.gnumeric_empty_sheet_count(EMPTY) == 1

    def test_gnumeric_has_empty_sheets_on_empty_sheet(self):
        assert _ga.gnumeric_has_empty_sheets(EMPTY) is True

    def test_gnumeric_sheet_count_on_empty_sheet(self):
        assert _ga.gnumeric_sheet_count(EMPTY) == 1


# ---------------------------------------------------------------------------
# gnumeric_sheet_analytics.py — source-based functions
# ---------------------------------------------------------------------------

SHEET_ANALYTICS_EXPECTED_MULTI = {
    "gnumeric_all_sheet_cell_counts": [4],
    "gnumeric_all_values": ["Name", "Score", "Alice", "42"],
    "gnumeric_avg_sheet_cell_count": 4.0,
    "gnumeric_cell_count": 4,
    "gnumeric_first_sheet_cell_count": 4,
    "gnumeric_first_sheet_name": "Sheet1",
    "gnumeric_has_data": True,
    "gnumeric_has_multiple_sheets": False,
    "gnumeric_has_numeric_values": True,
    "gnumeric_has_single_sheet": True,
    "gnumeric_is_empty_workbook": False,
    "gnumeric_is_gnumeric": True,
    "gnumeric_last_sheet_name": "Sheet1",
    "gnumeric_max_sheet_cell_count": 4,
    "gnumeric_min_sheet_cell_count": 4,
    "gnumeric_sheet_count": 1,
    "gnumeric_sheet_names_list": ["Sheet1"],
    "gnumeric_sheet_names_sorted": ["Sheet1"],
    "gnumeric_sheets_with_cells_count": 1,
    "gnumeric_sheets_with_data_count": 1,
    "gnumeric_total_numeric_value_count": 1,
    "gnumeric_total_unique_value_count": 4,
    "gnumeric_total_value_count": 4,
    "gnumeric_unique_value_count": 4,
}


class TestGnumericSheetAnalytics:
    @pytest.mark.parametrize(
        "func_name,expected", sorted(SHEET_ANALYTICS_EXPECTED_MULTI.items())
    )
    def test_sheet_analytics_function_on_multi_sample(self, func_name, expected):
        fn = getattr(_gsa, func_name)
        result = fn(MULTI)
        if isinstance(expected, list):
            assert sorted(result) == sorted(expected)
        else:
            assert result == expected

    def test_all_sheet_analytics_functions_are_covered(self):
        """Guards against new gnumeric_sheet_analytics.py functions shipping untested."""
        discovered = {
            name
            for name, _ in inspect.getmembers(_gsa, inspect.isfunction)
            if name.startswith("gnumeric_")
        }
        missing = discovered - set(SHEET_ANALYTICS_EXPECTED_MULTI)
        assert not missing, f"Uncovered gnumeric_sheet_analytics functions: {sorted(missing)}"

    def test_gnumeric_is_empty_workbook_on_empty_sheet(self):
        assert _gsa.gnumeric_is_empty_workbook(EMPTY) is True

    def test_gnumeric_has_data_on_empty_sheet(self):
        assert _gsa.gnumeric_has_data(EMPTY) is False

    def test_gnumeric_sheets_with_data_count_on_empty_sheet(self):
        assert _gsa.gnumeric_sheets_with_data_count(EMPTY) == 0


# ---------------------------------------------------------------------------
# GnumericDocument
# ---------------------------------------------------------------------------


class TestGnumericDocument:
    def test_from_file(self):
        doc = GnumericDocument.from_file(MULTI)
        assert doc.sheet_count == 1
        assert doc.cell_count == 4

    def test_sheet_count_and_cell_count(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.sheet_count == 1
        assert doc.cell_count == 4

    def test_sheets_property(self):
        doc = GnumericDocument(load(MULTI))
        assert len(doc.sheets) == 1
        assert doc.sheets[0]["name"] == "Sheet1"

    def test_is_gnumeric(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.is_gnumeric is True

    def test_get_sheet_valid_and_invalid_index(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.get_sheet(0) is not None
        assert doc.get_sheet(5) is None

    def test_get_sheet_names(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.get_sheet_names() == ["Sheet1"]

    def test_get_cell_value(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.get_cell_value(0, 0, 0) == "Name"
        assert doc.get_cell_value(5, 0, 0) == ""

    def test_is_empty(self):
        assert GnumericDocument(load(EMPTY)).is_empty is True
        assert GnumericDocument(load(MULTI)).is_empty is False

    def test_is_single_sheet_and_multi_sheet(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.is_single_sheet is True
        assert doc.is_multi_sheet is False

    def test_has_cells(self):
        assert GnumericDocument(load(MULTI)).has_cells is True
        assert GnumericDocument(load(EMPTY)).has_cells is False

    def test_avg_cells_per_sheet(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.avg_cells_per_sheet == 4.0

    def test_avg_cells_per_sheet_no_sheets(self):
        doc = GnumericDocument({"sheets": [], "sheet_count": 0, "cell_count": 0})
        assert doc.avg_cells_per_sheet == 0.0

    def test_is_sparse(self):
        assert GnumericDocument(load(EMPTY)).is_sparse is True
        assert GnumericDocument(load(MULTI)).is_sparse is False

    def test_is_large_workbook(self):
        assert GnumericDocument(load(MULTI)).is_large_workbook is False
        big = GnumericDocument({"sheets": [], "sheet_count": 1, "cell_count": 10001})
        assert big.is_large_workbook is True

    def test_has_many_sheets(self):
        assert GnumericDocument(load(MULTI)).has_many_sheets is False
        many = GnumericDocument({"sheets": [], "sheet_count": 6, "cell_count": 0})
        assert many.has_many_sheets is True

    def test_is_cell_dense(self):
        assert GnumericDocument(load(MULTI)).is_cell_dense is False
        dense = GnumericDocument({"sheets": [], "sheet_count": 1, "cell_count": 1001})
        assert dense.is_cell_dense is True

    def test_sheet_names_property(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.sheet_names == ["Sheet1"]

    def test_max_cells_per_sheet(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.max_cells_per_sheet == 4

    def test_max_cells_per_sheet_no_sheets(self):
        doc = GnumericDocument({"sheets": []})
        assert doc.max_cells_per_sheet == 0

    def test_is_valid_alias(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.is_valid == doc.is_gnumeric

    def test_min_cells_per_sheet(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.min_cells_per_sheet == 4

    def test_cell_count_range(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.cell_count_range == 0

    def test_cell_count_range_multi_sheet(self):
        model = add_sheet(load(MULTI), "Second")
        doc = GnumericDocument(model)
        assert doc.cell_count_range == 4  # 4 cells vs 0 cells

    def test_has_uniform_cell_distribution(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.has_uniform_cell_distribution is True

    def test_has_uniform_cell_distribution_false_when_varied(self):
        model = add_sheet(load(MULTI), "Second")
        doc = GnumericDocument(model)
        assert doc.has_uniform_cell_distribution is False

    def test_is_data_rich(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.is_data_rich is False

    def test_sheet_cell_variance(self):
        doc = GnumericDocument(load(MULTI))
        assert doc.sheet_cell_variance == 0.0

    def test_sheet_cell_variance_zero_max(self):
        doc = GnumericDocument({"sheets": [{"cell_grid": {}}], "sheet_count": 1, "cell_count": 0})
        assert doc.sheet_cell_variance == 0.0

    def test_has_large_sheets(self):
        assert GnumericDocument(load(MULTI)).has_large_sheets is False

    def test_set_cell_value_mutates_in_place(self):
        doc = GnumericDocument(load(MULTI))
        doc.set_cell_value(0, 0, 0, "Changed")
        assert doc.get_cell_value(0, 0, 0) == "Changed"

    def test_save_to_file(self):
        doc = GnumericDocument.from_file(MULTI)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "saved.gnumeric"
            doc.save_to_file(dest)
            assert dest.exists()
            reloaded = GnumericDocument.from_file(dest)
            assert reloaded.cell_count == doc.cell_count

    def test_save_to_file_roundtrips_mutation(self):
        doc = GnumericDocument.from_file(MULTI)
        doc.set_cell_value(0, 0, 0, "Mutated")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.gnumeric"
            doc.save_to_file(dest)
            reloaded = GnumericDocument.from_file(dest)
            assert reloaded.get_cell_value(0, 0, 0) == "Mutated"

    def test_save_to_file_empty_path_raises(self):
        doc = GnumericDocument.from_file(MULTI)
        with pytest.raises(CodecGnumericError):
            doc.save_to_file("")

    def test_to_dict(self):
        doc = GnumericDocument(load(MULTI))
        d = doc.to_dict()
        assert isinstance(d, dict)
        assert d["cell_count"] == 4

    def test_repr(self):
        doc = GnumericDocument(load(MULTI))
        text = repr(doc)
        assert "GnumericDocument" in text
        assert "sheet_count=1" in text
        assert "cell_count=4" in text


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------


class TestCodecExceptions:
    """gnumeric_codec.py's own GnumericError/GnumericParseError — these are
    the classes actually raised by load()/write_gnumeric()/etc at runtime."""

    def test_gnumeric_error_is_exception(self):
        assert issubclass(CodecGnumericError, Exception)

    def test_parse_error_inherits_from_error(self):
        assert issubclass(CodecGnumericParseError, CodecGnumericError)

    def test_load_raises_codec_parse_error(self):
        with pytest.raises(CodecGnumericParseError):
            load(b"garbage, not xml")

    def test_catchable_as_codec_base_error(self):
        with pytest.raises(CodecGnumericError):
            load(b"garbage, not xml")

    def test_message_preserved(self):
        err = CodecGnumericParseError("bad thing happened")
        assert str(err) == "bad thing happened"


class TestExceptionsModule:
    """gnumeric/exceptions.py's GnumericError/GnumericParseError/GnumericWriteError
    — a separate hierarchy rooted in FormatFactoryError, re-exported at package
    top-level as gnumeric.GnumericError / gnumeric.GnumericParseError."""

    def test_gnumeric_error_is_exception(self):
        assert issubclass(ExcGnumericError, Exception)

    def test_parse_error_inherits(self):
        assert issubclass(ExcGnumericParseError, ExcGnumericError)

    def test_write_error_inherits(self):
        assert issubclass(ExcGnumericWriteError, ExcGnumericError)

    def test_parse_error_message(self):
        err = ExcGnumericParseError("bad xml")
        assert str(err) == "bad xml"

    def test_write_error_message(self):
        err = ExcGnumericWriteError("write failed")
        assert str(err) == "write failed"

    def test_catchable_as_base(self):
        with pytest.raises(ExcGnumericError):
            raise ExcGnumericParseError("test")

    def test_write_error_catchable_as_base(self):
        with pytest.raises(ExcGnumericError):
            raise ExcGnumericWriteError("test")

    def test_package_top_level_aliases_exceptions_module(self):
        """gnumeric.GnumericError / gnumeric.GnumericParseError resolve to the
        exceptions.py hierarchy (the last `from .exceptions import *` in
        __init__.py wins over the earlier gnumeric_codec re-export)."""
        assert gnumeric.GnumericError is ExcGnumericError
        assert gnumeric.GnumericParseError is ExcGnumericParseError

    def test_instantiate_and_raise_top_level(self):
        with pytest.raises(gnumeric.GnumericError):
            raise gnumeric.GnumericParseError("boom")


# ---------------------------------------------------------------------------
# gnumeric_iter_sheets / Sheet spec class
# ---------------------------------------------------------------------------


class TestGnumericIterSheets:
    def test_yields_sheet_instances(self):
        sheets = list(gnumeric_iter_sheets(MULTI))
        assert len(sheets) == 1
        assert isinstance(sheets[0], Sheet)

    def test_sheet_name_and_cell_count(self):
        sheets = list(gnumeric_iter_sheets(MULTI))
        assert sheets[0].name == "Sheet1"
        assert sheets[0].cell_count == 4

    def test_sheet_cell_values(self):
        sheets = list(gnumeric_iter_sheets(MULTI))
        assert sorted(sheets[0].cell_values) == sorted(["Name", "Score", "Alice", "42"])

    def test_sheet_to_dict(self):
        sheets = list(gnumeric_iter_sheets(MULTI))
        d = sheets[0].to_dict()
        assert d["name"] == "Sheet1"

    def test_sheet_repr(self):
        sheets = list(gnumeric_iter_sheets(MULTI))
        text = repr(sheets[0])
        assert "Sheet1" in text
        assert "cell_count=4" in text

    def test_iterates_multiple_sheets(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "multi_sheet.gnumeric"
            model = add_sheet(load(MULTI), "Second")
            write_gnumeric(model, dest)
            names = [s.name for s in gnumeric_iter_sheets(dest)]
            assert names == ["Sheet1", "Second"]

    def test_empty_sheet_workbook(self):
        sheets = list(gnumeric_iter_sheets(EMPTY))
        assert len(sheets) == 1
        assert sheets[0].cell_count == 0

    def test_sheet_spec_metadata(self):
        assert Sheet.spec_qname == "gnumeric:sheet"
        assert Sheet.namespace_uri == "http://www.gnumeric.org/v10.dtd"
        assert "GnumericSheet" in Sheet.facade_names


# ---------------------------------------------------------------------------
# gnumeric_to_abw dogfood export
# ---------------------------------------------------------------------------


class TestGnumericToAbw:
    def test_converts_rows_to_paragraphs(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.abw"
            count = gnumeric_to_abw(MULTI, dest)
            assert count == 2
            assert dest.exists()

    def test_paragraph_separator(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.abw"
            gnumeric_to_abw(MULTI, dest, separator=" | ")
            content = dest.read_text(encoding="utf-8", errors="replace")
            assert "Name | Score" in content or "Name" in content

    def test_empty_sheet_produces_no_paragraphs(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.abw"
            count = gnumeric_to_abw(EMPTY, dest)
            assert count == 0
            assert dest.exists()

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "nested" / "dir" / "out.abw"
            gnumeric_to_abw(MULTI, dest)
            assert dest.exists()


# ---------------------------------------------------------------------------
# Task-named entry points that don't exist under those exact names
# ---------------------------------------------------------------------------


class TestNamedTargetsWithoutDirectExports:
    """The task brief names `load_gnumeric` and a standalone `roundtrip`
    among the target functions. Neither exists under those exact names in
    the gnumeric package (the equivalents are `load` and the load()/
    write_gnumeric() pair, both fully covered above) — recorded here via
    pytest.skip() per the skip-if-absent instruction rather than silently
    dropped."""

    def test_load_gnumeric_alias_absent(self):
        if hasattr(gnumeric, "load_gnumeric"):
            pytest.fail("gnumeric.load_gnumeric now exists — add direct coverage")
        pytest.skip("gnumeric package exports `load`, not `load_gnumeric`; "
                     "see TestLoadGnumeric for equivalent coverage.")

    def test_standalone_roundtrip_absent(self):
        if hasattr(gnumeric, "roundtrip"):
            pytest.fail("gnumeric.roundtrip now exists — add direct coverage")
        pytest.skip("gnumeric package has no standalone roundtrip(); "
                     "see TestCreateAndWriteGnumeric for load()+write_gnumeric() "
                     "roundtrip coverage.")
