"""
tests/python/ods/test_ods_gap_coverage.py

Comprehensive gap-closure test suite for the ODS (OpenDocument Spreadsheet)
FOSS Python track. Written to close ~88 missing_test_coverage gaps by
exercising every public export of src/python/ods/ against real sample
files.

Covers:
  - src/python/ods/ods_parser.py      (parse/probe + accessor/aggregate API)
  - src/python/ods/ods_writer.py      (bytes/file writer + in-memory mutation API)
  - src/python/ods/ods_csv_exporter.py (RFC 4180 CSV export)
  - src/python/ods/ods_stats.py       (dict-based + file-path-based stats)
  - src/python/ods/ods_analytics.py   (file-path-based analytics, canonical
                                        location per PCG-PORTFOLIO-002)
  - src/python/ods/models.py          (OdsModelDocument / OdsSheetModel / OdsCellModel)
  - src/python/ods/ods_workflow.py    (ods_installed_workflow)
  - src/python/ods/ods_sheet_iterator.py / ods_row_iterator.py (spec-shaped iterators)
  - src/python/ods/spec/table/*.py, spec/office/document.py (spec-shaped classes)
  - src/python/ods/exceptions.py, ods_parser.py exception hierarchy

Sample fixtures used (samples/by-format/ods/):
  valid/minimal-spreadsheet.ods  -- 1 sheet, 2 rows: ["Name","Value"], ["Alpha",42.0]
  valid/single-cell.ods          -- 1 sheet, 1 row, 1 cell: "A1"
  valid/numeric-row.ods          -- 1 sheet, 1 row, 3 numeric cells: [1.0, 2.0, 3.0]
  invalid/truncated.ods          -- not a valid ZIP container

NOTE on the ods_to_csv name collision: the ODS package exports a
`ods_to_csv(file_path, sheet_index=0) -> str` function from ods_parser.py,
but also ships a *separate* dogfood-export submodule `ods/ods_to_csv.py`
with a different signature (`ods_to_csv(src, dest) -> int`). Importing that
submodule anywhere in the test session rebinds the `ods.ods_to_csv`
package attribute to the submodule (Python import semantics), so this file
deliberately imports the parser's string-returning function directly from
`ods.ods_parser` rather than relying on the ambiguous `ods.ods_to_csv`
top-level attribute.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

import ods
from ods.ods_parser import (
    OdsCell,
    OdsDocument,
    OdsError,
    OdsInvalidContainerError,
    OdsRow,
    OdsSheet,
    OdsSizeError,
    get_capabilities,
    ods_to_csv as parser_ods_to_csv,
    ods_to_html,
    parse_ods,
    parse_ods_strict,
    probe_ods,
)
from ods.ods_writer import (
    add_row,
    add_sheet,
    delete_row,
    document_to_ods_bytes,
    remove_sheet,
    rename_sheet,
    set_cell_value,
    write_ods,
)
from ods.ods_csv_exporter import (
    OdsCsvExportError,
    export_ods_to_csv,
    export_ods_to_csv_file,
    get_csv_export_capabilities,
)
from ods.models import OdsCellModel, OdsDoc, OdsModelDocument, OdsSheetModel
from ods.ods_workflow import ods_installed_workflow
from ods.ods_sheet_iterator import ods_iter_sheets
from ods.ods_row_iterator import ods_iter_rows
from ods.spec.table.table import Table
from ods.spec.table.table_row import TableRow
from ods.spec.table.table_cell import TableCell
from ods.spec.office.document import Document
from ods.exceptions import (
    OdsError as ExcOdsError,
    OdsParseError,
    OdsWriteError,
)

_VALID_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_INVALID_DIR = _REPO / "samples" / "by-format" / "ods" / "invalid"

MINIMAL = str(_VALID_DIR / "minimal-spreadsheet.ods")
SINGLE = str(_VALID_DIR / "single-cell.ods")
NUMERIC = str(_VALID_DIR / "numeric-row.ods")
TRUNCATED = str(_INVALID_DIR / "truncated.ods")
NONEXISTENT = str(_VALID_DIR / "does-not-exist-xyz.ods")


def _close(actual, expected) -> bool:
    if isinstance(actual, float) or isinstance(expected, float):
        return math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-9)
    return actual == expected


# ---------------------------------------------------------------------------
# Package-level exports
# ---------------------------------------------------------------------------


class TestPackageExports:
    def test_version_present(self):
        assert isinstance(ods.__version__, str)

    def test_track_is_python_foss(self):
        assert ods.__track__ == "python-foss"

    def test_commercial_ready_false(self):
        assert ods.__commercial_ready__ is False

    def test_capability_level_present(self):
        assert isinstance(ods.__capability_level__, str)

    @pytest.mark.parametrize(
        "name",
        [
            "parse_ods",
            "parse_ods_strict",
            "probe_ods",
            "get_cell_value",
            "get_sheet_names",
            "get_row_count",
            "get_column_count",
            "get_row_values",
            "count_sheets",
            "get_all_values",
            "get_cell_count",
            "sum_column",
            "filter_rows_by_value",
            "get_column_values",
            "average_column",
            "max_column_value",
            "min_column_value",
            "ods_to_html",
            "get_sheet_as_dict_list",
            "count_nonempty_cells",
            "count_distinct_values",
            "sum_row",
            "write_ods",
            "document_to_ods_bytes",
            "set_cell_value",
            "add_sheet",
            "remove_sheet",
            "rename_sheet",
            "add_row",
            "delete_row",
            "spreadsheet_stats",
            "sheet_name_order",
            "OdsModelDocument",
            "ods_installed_workflow",
            "ods_iter_sheets",
            "ods_iter_rows",
        ],
    )
    def test_export_present(self, name):
        assert hasattr(ods, name), f"expected {name!r} in ods package exports"

    def test_all_contains_no_dunders(self):
        assert all(not n.startswith("_") for n in ods.__all__)


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)

    def test_format_is_ods(self):
        assert get_capabilities()["format"] == "ods"

    def test_gate_is_5(self):
        assert get_capabilities()["gate"] == 5

    def test_commercial_product_ready_false(self):
        assert get_capabilities()["commercial_product_ready"] is False

    def test_supported_and_unsupported_disjoint(self):
        caps = get_capabilities()
        supported = set(caps["supported"])
        unsupported = set(caps["unsupported"])
        assert supported.isdisjoint(unsupported)

    def test_size_limits_present(self):
        caps = get_capabilities()
        assert caps["max_file_size"] == 64 * 1024 * 1024
        assert caps["max_zip_entries"] == 1000
        assert caps["max_columns"] == 1024
        assert caps["max_rows"] == 1048576


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


class TestDataclasses:
    def test_ods_cell_defaults(self):
        cell = OdsCell()
        assert cell.value is None
        assert cell.value_type == ""
        assert cell.text == ""

    def test_ods_cell_spec_qname(self):
        assert OdsCell.spec_qname == "table:table-cell"

    def test_ods_row_defaults(self):
        row = OdsRow()
        assert row.cells == []

    def test_ods_row_spec_qname(self):
        assert OdsRow.spec_qname == "table:table-row"

    def test_ods_sheet_defaults(self):
        sheet = OdsSheet()
        assert sheet.name == ""
        assert sheet.rows == []

    def test_ods_sheet_spec_qname(self):
        assert OdsSheet.spec_qname == "table:table"

    def test_ods_document_defaults(self):
        doc = OdsDocument()
        assert doc.sheets == []
        assert doc.path == ""

    def test_ods_document_spec_qname(self):
        assert OdsDocument.spec_qname == "office:document"

    def test_ods_document_construction(self):
        sheet = OdsSheet(name="S1", rows=[OdsRow(cells=[OdsCell(value=1.0, value_type="float", text="1")])])
        doc = OdsDocument(sheets=[sheet], path="x.ods")
        assert doc.sheets[0].name == "S1"
        assert doc.sheets[0].rows[0].cells[0].value == 1.0


# ---------------------------------------------------------------------------
# parse_ods_strict / parse_ods / probe_ods
# ---------------------------------------------------------------------------


class TestParseOdsStrict:
    @pytest.mark.parametrize("path", [MINIMAL, SINGLE, NUMERIC])
    def test_returns_ods_document(self, path):
        doc = parse_ods_strict(path)
        assert isinstance(doc, OdsDocument)

    def test_minimal_sheet_count(self):
        doc = parse_ods_strict(MINIMAL)
        assert len(doc.sheets) == 1

    def test_minimal_sheet_name(self):
        doc = parse_ods_strict(MINIMAL)
        assert doc.sheets[0].name == "Sheet1"

    def test_minimal_row_count(self):
        doc = parse_ods_strict(MINIMAL)
        assert len(doc.sheets[0].rows) == 2

    def test_minimal_cell_values(self):
        doc = parse_ods_strict(MINIMAL)
        row0 = doc.sheets[0].rows[0]
        row1 = doc.sheets[0].rows[1]
        assert [c.value for c in row0.cells] == ["Name", "Value"]
        assert [c.value for c in row1.cells] == ["Alpha", 42.0]

    def test_minimal_value_types(self):
        doc = parse_ods_strict(MINIMAL)
        row1 = doc.sheets[0].rows[1]
        assert row1.cells[0].value_type == "string"
        assert row1.cells[1].value_type == "float"

    def test_numeric_row_all_float(self):
        doc = parse_ods_strict(NUMERIC)
        vals = [c.value for c in doc.sheets[0].rows[0].cells]
        assert vals == [1.0, 2.0, 3.0]

    def test_single_cell(self):
        doc = parse_ods_strict(SINGLE)
        assert len(doc.sheets[0].rows) == 1
        assert doc.sheets[0].rows[0].cells[0].value == "A1"

    def test_path_recorded(self):
        doc = parse_ods_strict(MINIMAL)
        assert doc.path == MINIMAL

    def test_truncated_raises_invalid_container(self):
        with pytest.raises(OdsInvalidContainerError):
            parse_ods_strict(TRUNCATED)

    def test_truncated_error_is_ods_error(self):
        with pytest.raises(OdsError):
            parse_ods_strict(TRUNCATED)

    def test_nonexistent_raises(self):
        with pytest.raises(OSError):
            parse_ods_strict(NONEXISTENT)

    def test_accepts_path_object(self):
        doc = parse_ods_strict(Path(MINIMAL))
        assert len(doc.sheets) == 1


class TestParseOdsDict:
    def test_minimal_ok_true(self):
        result = parse_ods(MINIMAL)
        assert result["ok"] is True

    def test_minimal_sheet_count(self):
        result = parse_ods(MINIMAL)
        assert result["sheet_count"] == 1

    def test_minimal_structure(self):
        result = parse_ods(MINIMAL)
        sheet = result["sheets"][0]
        assert sheet["name"] == "Sheet1"
        assert sheet["row_count"] == 2
        assert sheet["rows"][1]["cells"][1]["value"] == 42.0

    def test_truncated_ok_false(self):
        result = parse_ods(TRUNCATED)
        assert result["ok"] is False
        assert result["error_type"] == "OdsInvalidContainerError"

    def test_nonexistent_ok_false(self):
        result = parse_ods(NONEXISTENT)
        assert result["ok"] is False
        assert "error" in result

    def test_never_raises_on_bad_input(self):
        # parse_ods() contract: never raises, always returns a dict.
        for bad in (TRUNCATED, NONEXISTENT):
            result = parse_ods(bad)
            assert isinstance(result, dict)


class TestProbeOds:
    def test_valid_file_probe(self):
        result = probe_ods(MINIMAL)
        assert result["exists"] is True
        assert result["valid_container"] is True
        assert "mimetype" in result
        assert result["mimetype"] == "application/vnd.oasis.opendocument.spreadsheet"

    def test_valid_file_entries_present(self):
        result = probe_ods(MINIMAL)
        assert "mimetype" in result["entries"]
        assert "content.xml" in result["entries"]

    def test_truncated_probe(self):
        result = probe_ods(TRUNCATED)
        assert result["exists"] is True
        assert result["valid_container"] is False
        assert "error" in result

    def test_nonexistent_probe(self):
        result = probe_ods(NONEXISTENT)
        assert result["exists"] is False
        assert "valid_container" not in result


# ---------------------------------------------------------------------------
# Cell / row / sheet accessors (ods_parser.py Rnext15 API)
# ---------------------------------------------------------------------------


class TestCellRowSheetAccessors:
    def test_get_cell_value_string(self):
        assert ods.get_cell_value(MINIMAL, 0, 0, 0) == "Name"

    def test_get_cell_value_float(self):
        assert ods.get_cell_value(MINIMAL, 0, 1, 1) == 42.0

    def test_get_sheet_names(self):
        assert ods.get_sheet_names(MINIMAL) == ["Sheet1"]

    def test_get_row_count(self):
        assert ods.get_row_count(MINIMAL) == 2

    def test_get_row_count_default_sheet_index(self):
        assert ods.get_row_count(NUMERIC) == 1

    def test_get_column_count(self):
        assert ods.get_column_count(MINIMAL) == 2

    def test_get_column_count_numeric(self):
        assert ods.get_column_count(NUMERIC) == 3

    def test_get_row_values_header(self):
        assert ods.get_row_values(MINIMAL, 0, 0) == ["Name", "Value"]

    def test_get_row_values_data(self):
        assert ods.get_row_values(MINIMAL, 0, 1) == ["Alpha", 42.0]

    def test_count_sheets(self):
        assert ods.count_sheets(MINIMAL) == 1

    def test_get_all_values(self):
        assert ods.get_all_values(MINIMAL) == ["Name", "Value", "Alpha", 42.0]

    def test_get_cell_count(self):
        assert ods.get_cell_count(MINIMAL) == 4

    def test_get_cell_count_numeric(self):
        assert ods.get_cell_count(NUMERIC) == 3


class TestOutOfRangeAccessors:
    def test_get_cell_value_sheet_out_of_range(self):
        assert ods.get_cell_value(MINIMAL, 5, 0, 0) is None

    def test_get_cell_value_row_out_of_range(self):
        assert ods.get_cell_value(MINIMAL, 0, 99, 0) is None

    def test_get_cell_value_col_out_of_range(self):
        assert ods.get_cell_value(MINIMAL, 0, 0, 99) is None

    def test_get_row_count_sheet_out_of_range(self):
        assert ods.get_row_count(MINIMAL, sheet_index=5) == 0

    def test_get_column_count_sheet_out_of_range(self):
        assert ods.get_column_count(MINIMAL, sheet_index=5) == 0

    def test_get_row_values_sheet_out_of_range(self):
        assert ods.get_row_values(MINIMAL, 5, 0) == []

    def test_get_row_values_row_out_of_range(self):
        assert ods.get_row_values(MINIMAL, 0, 99) == []

    def test_get_all_values_sheet_out_of_range(self):
        assert ods.get_all_values(MINIMAL, sheet_index=5) == []

    def test_get_cell_count_sheet_out_of_range(self):
        assert ods.get_cell_count(MINIMAL, sheet_index=5) == 0


# ---------------------------------------------------------------------------
# Column / row aggregate functions
# ---------------------------------------------------------------------------


class TestColumnAndRowAggregates:
    def test_sum_column(self):
        assert ods.sum_column(MINIMAL, 1) == 42.0

    def test_sum_column_no_numeric(self):
        assert ods.sum_column(MINIMAL, 0) == 0.0

    def test_sum_column_out_of_range_sheet(self):
        assert ods.sum_column(MINIMAL, 1, sheet_index=5) == 0.0

    def test_get_column_values(self):
        assert ods.get_column_values(MINIMAL, 1) == ["Value", 42.0]

    def test_get_column_values_missing_cells_are_none(self):
        # numeric-row.ods has 3 columns; asking for col 5 should return None per row.
        assert ods.get_column_values(NUMERIC, 5) == [None]

    def test_average_column(self):
        assert ods.average_column(MINIMAL, 1) == 42.0

    def test_average_column_no_numeric(self):
        assert ods.average_column(MINIMAL, 0) == 0.0

    def test_max_column_value(self):
        assert ods.max_column_value(MINIMAL, 1) == 42.0

    def test_max_column_value_no_numeric(self):
        assert ods.max_column_value(MINIMAL, 0) is None

    def test_min_column_value(self):
        assert ods.min_column_value(MINIMAL, 1) == 42.0

    def test_min_column_value_no_numeric(self):
        assert ods.min_column_value(MINIMAL, 0) is None

    def test_filter_rows_by_value_match(self):
        result = ods.filter_rows_by_value(MINIMAL, 0, "Alpha")
        assert result == [["Alpha", 42.0]]

    def test_filter_rows_by_value_no_match(self):
        result = ods.filter_rows_by_value(MINIMAL, 0, "NoSuchValue")
        assert result == []

    def test_filter_rows_by_value_out_of_range_sheet(self):
        assert ods.filter_rows_by_value(MINIMAL, 0, "Alpha", sheet_index=5) == []

    def test_count_distinct_values(self):
        assert ods.count_distinct_values(MINIMAL, 0) == 2

    def test_count_distinct_values_numeric(self):
        assert ods.count_distinct_values(NUMERIC, 0) == 1

    def test_sum_row(self):
        assert ods.sum_row(MINIMAL, 1) == 42.0

    def test_sum_row_header_row(self):
        assert ods.sum_row(MINIMAL, 0) == 0.0

    def test_sum_row_numeric(self):
        assert ods.sum_row(NUMERIC, 0) == 6.0

    def test_sum_row_out_of_range(self):
        assert ods.sum_row(MINIMAL, 99) == 0.0

    def test_sum_row_out_of_range_sheet(self):
        assert ods.sum_row(MINIMAL, 0, sheet_index=5) == 0.0


class TestSheetAsDictList:
    def test_minimal_produces_one_record(self):
        records = ods.get_sheet_as_dict_list(MINIMAL)
        assert records == [{"Name": "Alpha", "Value": 42.0}]

    def test_single_row_sheet_returns_empty(self):
        assert ods.get_sheet_as_dict_list(SINGLE) == []

    def test_numeric_row_sheet_returns_empty(self):
        assert ods.get_sheet_as_dict_list(NUMERIC) == []

    def test_out_of_range_sheet_returns_empty(self):
        assert ods.get_sheet_as_dict_list(MINIMAL, sheet_index=5) == []

    def test_count_nonempty_cells(self):
        assert ods.count_nonempty_cells(MINIMAL) == 4

    def test_count_nonempty_cells_out_of_range(self):
        assert ods.count_nonempty_cells(MINIMAL, sheet_index=5) == 0


# ---------------------------------------------------------------------------
# CSV / HTML export (ods_parser.py string-returning helpers)
# ---------------------------------------------------------------------------


class TestParserCsvHtmlExport:
    def test_ods_to_csv_minimal(self):
        assert parser_ods_to_csv(MINIMAL) == "Name,Value\r\nAlpha,42\r\n"

    def test_ods_to_csv_out_of_range_sheet(self):
        assert parser_ods_to_csv(MINIMAL, sheet_index=5) == ""

    def test_ods_to_csv_numeric_row(self):
        assert parser_ods_to_csv(NUMERIC) == "1,2,3\r\n"

    def test_ods_to_html_minimal(self):
        html = ods_to_html(MINIMAL)
        assert html.startswith("<table>")
        assert html.endswith("</table>")
        assert "<td>Name</td>" in html
        assert "<td>42</td>" in html

    def test_ods_to_html_out_of_range_sheet(self):
        assert ods_to_html(MINIMAL, sheet_index=5) == ""


class TestCsvExporterModule:
    def test_export_ods_to_csv_minimal(self):
        doc = parse_ods_strict(MINIMAL)
        assert export_ods_to_csv(doc) == "Name,Value\r\nAlpha,42\r\n"

    def test_export_ods_to_csv_numeric(self):
        doc = parse_ods_strict(NUMERIC)
        assert export_ods_to_csv(doc) == "1,2,3\r\n"

    def test_export_needs_quoting_field(self):
        doc = OdsDocument(
            sheets=[
                OdsSheet(
                    name="S1",
                    rows=[
                        OdsRow(
                            cells=[
                                OdsCell(value="a,b", value_type="string", text="a,b"),
                                OdsCell(value='say "hi"', value_type="string", text='say "hi"'),
                            ]
                        )
                    ],
                )
            ]
        )
        csv_text = export_ods_to_csv(doc)
        assert '"a,b"' in csv_text
        assert '"say ""hi"""' in csv_text

    def test_export_out_of_range_sheet_raises(self):
        doc = parse_ods_strict(MINIMAL)
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc, sheet_index=99)

    def test_export_no_sheets_raises(self):
        empty = OdsDocument(sheets=[], path="x")
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(empty)

    def test_export_ods_to_csv_file(self, tmp_path):
        doc = parse_ods_strict(MINIMAL)
        dest = tmp_path / "out.csv"
        result_path = export_ods_to_csv_file(doc, dest)
        assert Path(result_path).exists()
        # Read with newline="" to preserve the file's literal CRLF line endings
        # (Path.read_text() would otherwise apply universal-newline translation).
        assert Path(result_path).read_text(encoding="utf-8", newline="") == "Name,Value\r\nAlpha,42\r\n"

    def test_export_ods_to_csv_file_include_empty_rows(self, tmp_path):
        doc = OdsDocument(sheets=[OdsSheet(name="S1", rows=[OdsRow(cells=[])])])
        dest = tmp_path / "empty.csv"
        export_ods_to_csv_file(doc, dest, include_empty_rows=True)
        assert dest.exists()

    def test_get_csv_export_capabilities(self):
        caps = get_csv_export_capabilities()
        assert caps["format"] == "ods"
        assert caps["export_target"] == "csv"
        assert caps["rfc"] == "RFC 4180"
        assert "single_sheet_only" in caps["limitations"]


# ---------------------------------------------------------------------------
# Writer -- serialization
# ---------------------------------------------------------------------------


class TestWriterCore:
    def test_document_to_ods_bytes_returns_bytes(self):
        doc = parse_ods_strict(MINIMAL)
        data = document_to_ods_bytes(doc)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_document_to_ods_bytes_is_zip(self):
        import zipfile
        import io
        doc = parse_ods_strict(MINIMAL)
        data = document_to_ods_bytes(doc)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
        assert "mimetype" in names
        assert "content.xml" in names
        assert "META-INF/manifest.xml" in names

    def test_write_ods_creates_file(self, tmp_path):
        doc = parse_ods_strict(MINIMAL)
        dest = tmp_path / "written.ods"
        write_ods(doc, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_roundtrip_preserves_sheet_names(self, tmp_path):
        doc = parse_ods_strict(MINIMAL)
        dest = tmp_path / "roundtrip.ods"
        write_ods(doc, dest)
        reparsed = parse_ods_strict(dest)
        assert [s.name for s in reparsed.sheets] == [s.name for s in doc.sheets]

    def test_roundtrip_preserves_cell_values(self, tmp_path):
        doc = parse_ods_strict(MINIMAL)
        dest = tmp_path / "roundtrip2.ods"
        write_ods(doc, dest)
        reparsed = parse_ods_strict(dest)
        original_values = [c.value for r in doc.sheets[0].rows for c in r.cells]
        new_values = [c.value for r in reparsed.sheets[0].rows for c in r.cells]
        assert new_values == original_values

    def test_roundtrip_multisheet(self, tmp_path):
        doc = OdsDocument(
            sheets=[
                OdsSheet(name="A", rows=[OdsRow(cells=[OdsCell(value="x", value_type="string", text="x")])]),
                OdsSheet(name="B", rows=[OdsRow(cells=[OdsCell(value=1.0, value_type="float", text="1")])]),
            ]
        )
        dest = tmp_path / "multi.ods"
        write_ods(doc, dest)
        reparsed = parse_ods_strict(dest)
        assert [s.name for s in reparsed.sheets] == ["A", "B"]
        assert reparsed.sheets[1].rows[0].cells[0].value == 1.0


class TestWriterMutations:
    def _fresh(self):
        return parse_ods_strict(MINIMAL)

    def test_set_cell_value_success(self):
        doc = self._fresh()
        ok, msg = set_cell_value(doc, 0, 0, 0, "Changed")
        assert ok is True
        assert doc.sheets[0].rows[0].cells[0].value == "Changed"

    def test_set_cell_value_extends_rows_and_cells(self):
        doc = self._fresh()
        ok, _ = set_cell_value(doc, 0, 10, 10, "far", "string")
        assert ok is True
        assert len(doc.sheets[0].rows) == 11
        assert doc.sheets[0].rows[10].cells[10].value == "far"

    def test_set_cell_value_out_of_range_sheet(self):
        doc = self._fresh()
        ok, msg = set_cell_value(doc, 5, 0, 0, "x")
        assert ok is False
        assert "out of range" in msg

    def test_add_sheet_success(self):
        doc = self._fresh()
        ok, msg = add_sheet(doc, "NewSheet")
        assert ok is True
        assert doc.sheets[-1].name == "NewSheet"

    def test_add_sheet_duplicate_fails(self):
        doc = self._fresh()
        ok, msg = add_sheet(doc, "Sheet1")
        assert ok is False
        assert "already exists" in msg

    def test_add_sheet_at_position(self):
        doc = self._fresh()
        add_sheet(doc, "First", position=0)
        assert doc.sheets[0].name == "First"

    def test_remove_sheet_success(self):
        doc = self._fresh()
        add_sheet(doc, "ToRemove")
        ok, msg = remove_sheet(doc, "ToRemove")
        assert ok is True
        assert "ToRemove" not in [s.name for s in doc.sheets]

    def test_remove_sheet_missing_fails(self):
        doc = self._fresh()
        ok, msg = remove_sheet(doc, "NoSuchSheet")
        assert ok is False
        assert "not found" in msg

    def test_rename_sheet_success(self):
        doc = self._fresh()
        ok, msg = rename_sheet(doc, "Sheet1", "Renamed")
        assert ok is True
        assert doc.sheets[0].name == "Renamed"

    def test_rename_sheet_missing_source_fails(self):
        doc = self._fresh()
        ok, msg = rename_sheet(doc, "NoSuchSheet", "X")
        assert ok is False
        assert "not found" in msg

    def test_rename_sheet_duplicate_target_fails(self):
        doc = self._fresh()
        add_sheet(doc, "Other")
        ok, msg = rename_sheet(doc, "Sheet1", "Other")
        assert ok is False
        assert "already exists" in msg

    def test_add_row_success(self):
        doc = self._fresh()
        before = len(doc.sheets[0].rows)
        ok, msg = add_row(doc, 0, ["x", 1, 2.5])
        assert ok is True
        assert len(doc.sheets[0].rows) == before + 1
        assert len(doc.sheets[0].rows[-1].cells) == 3

    def test_add_row_numeric_values_get_float_type(self):
        doc = self._fresh()
        add_row(doc, 0, [7])
        cell = doc.sheets[0].rows[-1].cells[0]
        assert cell.value_type == "float"

    def test_add_row_out_of_range_sheet(self):
        doc = self._fresh()
        ok, msg = add_row(doc, 5, ["x"])
        assert ok is False
        assert "out of range" in msg

    def test_delete_row_success(self):
        doc = self._fresh()
        before = len(doc.sheets[0].rows)
        ok, msg = delete_row(doc, 0, 0)
        assert ok is True
        assert len(doc.sheets[0].rows) == before - 1

    def test_delete_row_out_of_range(self):
        doc = self._fresh()
        ok, msg = delete_row(doc, 0, 999)
        assert ok is False
        assert "out of range" in msg

    def test_delete_row_out_of_range_sheet(self):
        doc = self._fresh()
        ok, msg = delete_row(doc, 99, 0)
        assert ok is False
        assert "out of range" in msg

    def test_mutation_then_roundtrip(self, tmp_path):
        doc = self._fresh()
        add_sheet(doc, "Extra")
        add_row(doc, 1, ["p", "q"])
        set_cell_value(doc, 0, 0, 0, "EditedHeader")
        dest = tmp_path / "mutated.ods"
        write_ods(doc, dest)
        reparsed = parse_ods_strict(dest)
        assert [s.name for s in reparsed.sheets] == ["Sheet1", "Extra"]
        assert reparsed.sheets[0].rows[0].cells[0].value == "EditedHeader"
        assert reparsed.sheets[1].rows[0].cells[0].value == "p"


# ---------------------------------------------------------------------------
# ods_stats.py -- dict-based functions (operate on parse_ods() output)
# ---------------------------------------------------------------------------


class TestStatsDictBased:
    def test_spreadsheet_stats_minimal(self):
        result = ods.spreadsheet_stats(parse_ods(MINIMAL))
        assert result["sheet_count"] == 1
        assert result["total_rows"] == 2
        assert result["total_cells"] == 4
        assert result["non_empty_cells"] == 4
        assert result["per_sheet"][0]["name"] == "Sheet1"

    def test_spreadsheet_stats_empty_doc(self):
        result = ods.spreadsheet_stats({"sheets": []})
        assert result == {
            "sheet_count": 0,
            "total_rows": 0,
            "total_cells": 0,
            "non_empty_cells": 0,
            "per_sheet": [],
        }

    def test_sheet_name_order(self):
        assert ods.sheet_name_order(parse_ods(MINIMAL)) == ["Sheet1"]

    def test_sheet_name_order_defaults_when_unnamed(self):
        doc = {"sheets": [{"rows": []}]}
        assert ods.sheet_name_order(doc) == ["Sheet1"]

    def test_ods_cell_type_distribution_minimal(self):
        result = ods.ods_cell_type_distribution(parse_ods(MINIMAL))
        assert result["total_cells"] == 4
        assert result["by_type"]["text"] == 3
        assert result["by_type"]["numeric"] == 1
        assert result["empty_fraction"] == 0.0

    def test_ods_cell_type_distribution_empty_cell(self):
        doc = {"sheets": [{"rows": [{"cells": [{"value": None, "text": ""}]}]}]}
        result = ods.ods_cell_type_distribution(doc)
        assert result["by_type"]["empty"] == 1
        assert result["empty_fraction"] == 1.0

    def test_ods_sheet_name_list(self):
        assert ods.ods_sheet_name_list(parse_ods(MINIMAL)) == ["Sheet1"]

    def test_ods_sheet_name_list_no_sheets_key(self):
        assert ods.ods_sheet_name_list({}) == []

    def test_ods_formula_cell_count_zero(self):
        assert ods.ods_formula_cell_count(parse_ods(MINIMAL)) == 0

    def test_ods_formula_cell_count_present(self):
        doc = {
            "sheets": [
                {"rows": [{"cells": [{"value": 1, "formula": "=A1+1"}, {"value": 2}]}]}
            ]
        }
        assert ods.ods_formula_cell_count(doc) == 1

    def test_ods_data_validation_count_zero(self):
        assert ods.ods_data_validation_count(parse_ods(MINIMAL)) == 0

    def test_ods_data_validation_count_doc_level_list(self):
        doc = {"data_validations": [{"name": "v1"}, {"name": "v2"}]}
        assert ods.ods_data_validation_count(doc) == 2

    def test_ods_data_validation_count_cell_level(self):
        doc = {
            "sheets": [
                {
                    "rows": [
                        {"cells": [{"validation": "rule1"}, {"validation": "rule1"}, {"validation": "rule2"}]}
                    ]
                }
            ]
        }
        # rule1 counted once (dedup by name), rule2 once => 2
        assert ods.ods_data_validation_count(doc) == 2


# ---------------------------------------------------------------------------
# File-path-based analytics / stats functions (ods_stats.py + ods_analytics.py)
#
# Table-driven regression coverage: every one of these functions is invoked
# against all three valid sample files and checked against the function's
# actual, hand-verified current behavior. Values below were independently
# derived from the known sample contents:
#   minimal-spreadsheet.ods -> 1 sheet, rows=[["Name","Value"],["Alpha",42.0]]
#   single-cell.ods         -> 1 sheet, rows=[["A1"]]
#   numeric-row.ods         -> 1 sheet, rows=[[1.0, 2.0, 3.0]]
# ---------------------------------------------------------------------------

EXPECTED_ANALYTICS = {
    "minimal": {
        "ods_has_data": True,
        "ods_first_sheet_name": "Sheet1",
        "ods_total_row_count": 2,
        "ods_unique_sheet_names": ["Sheet1"],
        "ods_has_float_cells": True,
        "ods_max_sheet_row_count": 2,
        "ods_sheet_names_sorted": ["Sheet1"],
        "ods_has_single_sheet": True,
        "ods_first_sheet_row_count": 2,
        "ods_all_sheets_named": True,
        "ods_has_uniform_sheet_row_count": True,
        "ods_min_sheet_row_count": 2,
        "ods_sheet_count": 1,
        "ods_has_sheets": True,
        "ods_max_sheet_name_length": 6,
        "ods_last_sheet_name": "Sheet1",
        "ods_avg_sheet_row_count": 2.0,
        "ods_total_cell_count": 4,
        "ods_is_multi_sheet": False,
        "ods_last_sheet_row_count": 2,
        "ods_has_text_cells": True,
        "ods_sheet_names_list": ["Sheet1"],
        "ods_max_row_length": 2,
        "ods_numeric_cell_count": 1,
        "ods_string_cell_count": 3,
        "ods_row_count": 2,
        "ods_empty_cell_count": 0,
        "ods_column_count": 2,
        "ods_empty_row_count": 0,
        "ods_has_merged_cells": False,
        "ods_numeric_density": 0.25,
        "ods_average_cells_per_row": 2.0,
        "ods_has_empty_rows": False,
        "ods_merged_cell_count": 0,
        "ods_avg_cells_per_sheet": 4.0,
        "ods_data_density": 1.0,
        "ods_max_cell_value_length": 5,
        "ods_min_cell_value_length": 4,
        "ods_all_sheets_have_data": True,
        "ods_is_single_sheet": True,
        "ods_string_density": 0.75,
        "ods_max_numeric_value": 42.0,
        "ods_has_string_cells": True,
        "ods_min_numeric_value": 42.0,
        "ods_has_numeric_cells": True,
        "ods_nonempty_row_count": 2,
        "ods_is_empty": False,
        "ods_is_single_row": False,
        "ods_avg_row_length": 2.0,
        "ods_nonempty_cell_count": 4,
        "ods_cell_value_variance": 0.0,
        "ods_column_value_variance": 0.0,
        "ods_has_formulas": False,
        "ods_row_value_variance": 0.0,
        "ods_is_single_cell": False,
        "ods_is_rectangular": True,
        "ods_total_string_length": 14,
        "ods_is_all_numeric": False,
        "ods_empty_sheet_count": 0,
        "ods_numeric_sum": 42.0,
        "ods_min_row_length": 2,
        "ods_avg_numeric_value": 42.0,
        "ods_nonempty_row_ratio": 1.0,
        "ods_longest_row_index": 0,
        "ods_numeric_sum_all": 42.0,
        "ods_empty_column_count": 0,
        "ods_max_numeric_sum": 42.0,
        "ods_cell_density": 2.0,
        "ods_numeric_ratio": 0.25,
        "ods_is_square": True,
        "ods_numeric_column_count": 1,
        "ods_row_cell_variance": 0.0,
        "ods_string_cell_ratio": 0.75,
        "ods_widest_column_index": 0,
        "ods_numeric_cell_ratio": 0.25,
        "ods_column_fill_rate": 1.0,
        "ods_value_type_count": 2,
        "ods_nonempty_cell_percentage": 1.0,
    },
    "single": {
        "ods_has_data": True,
        "ods_first_sheet_name": "Sheet1",
        "ods_total_row_count": 1,
        "ods_unique_sheet_names": ["Sheet1"],
        "ods_has_float_cells": False,
        "ods_max_sheet_row_count": 1,
        "ods_sheet_names_sorted": ["Sheet1"],
        "ods_has_single_sheet": True,
        "ods_first_sheet_row_count": 1,
        "ods_all_sheets_named": True,
        "ods_has_uniform_sheet_row_count": True,
        "ods_min_sheet_row_count": 1,
        "ods_sheet_count": 1,
        "ods_has_sheets": True,
        "ods_max_sheet_name_length": 6,
        "ods_last_sheet_name": "Sheet1",
        "ods_avg_sheet_row_count": 1.0,
        "ods_total_cell_count": 1,
        "ods_is_multi_sheet": False,
        "ods_last_sheet_row_count": 1,
        "ods_has_text_cells": True,
        "ods_sheet_names_list": ["Sheet1"],
        "ods_max_row_length": 1,
        "ods_numeric_cell_count": 0,
        "ods_string_cell_count": 1,
        "ods_row_count": 1,
        "ods_empty_cell_count": 0,
        "ods_column_count": 1,
        "ods_empty_row_count": 0,
        "ods_has_merged_cells": False,
        "ods_numeric_density": 0.0,
        "ods_average_cells_per_row": 1.0,
        "ods_has_empty_rows": False,
        "ods_merged_cell_count": 0,
        "ods_avg_cells_per_sheet": 1.0,
        "ods_data_density": 1.0,
        "ods_max_cell_value_length": 2,
        "ods_min_cell_value_length": 2,
        "ods_all_sheets_have_data": True,
        "ods_is_single_sheet": True,
        "ods_string_density": 1.0,
        "ods_max_numeric_value": None,
        "ods_has_string_cells": True,
        "ods_min_numeric_value": None,
        "ods_has_numeric_cells": False,
        "ods_nonempty_row_count": 1,
        "ods_is_empty": False,
        "ods_is_single_row": True,
        "ods_avg_row_length": 1.0,
        "ods_nonempty_cell_count": 1,
        "ods_cell_value_variance": 0.0,
        "ods_column_value_variance": 0.0,
        "ods_has_formulas": False,
        "ods_row_value_variance": 0.0,
        "ods_is_single_cell": True,
        "ods_is_rectangular": True,
        "ods_total_string_length": 2,
        "ods_is_all_numeric": False,
        "ods_empty_sheet_count": 0,
        "ods_numeric_sum": 0.0,
        "ods_min_row_length": 1,
        "ods_avg_numeric_value": 0.0,
        "ods_nonempty_row_ratio": 1.0,
        "ods_longest_row_index": 0,
        "ods_numeric_sum_all": 0.0,
        "ods_empty_column_count": 0,
        "ods_max_numeric_sum": 0.0,
        "ods_cell_density": 1.0,
        "ods_numeric_ratio": 0.0,
        "ods_is_square": True,
        "ods_numeric_column_count": 0,
        "ods_row_cell_variance": 0.0,
        "ods_string_cell_ratio": 1.0,
        "ods_widest_column_index": 0,
        "ods_numeric_cell_ratio": 0.0,
        "ods_column_fill_rate": 1.0,
        "ods_value_type_count": 1,
        "ods_nonempty_cell_percentage": 1.0,
    },
    "numeric": {
        "ods_has_data": True,
        "ods_first_sheet_name": "Sheet1",
        "ods_total_row_count": 1,
        "ods_unique_sheet_names": ["Sheet1"],
        "ods_has_float_cells": True,
        "ods_max_sheet_row_count": 1,
        "ods_sheet_names_sorted": ["Sheet1"],
        "ods_has_single_sheet": True,
        "ods_first_sheet_row_count": 1,
        "ods_all_sheets_named": True,
        "ods_has_uniform_sheet_row_count": True,
        "ods_min_sheet_row_count": 1,
        "ods_sheet_count": 1,
        "ods_has_sheets": True,
        "ods_max_sheet_name_length": 6,
        "ods_last_sheet_name": "Sheet1",
        "ods_avg_sheet_row_count": 1.0,
        "ods_total_cell_count": 3,
        "ods_is_multi_sheet": False,
        "ods_last_sheet_row_count": 1,
        "ods_has_text_cells": True,
        "ods_sheet_names_list": ["Sheet1"],
        "ods_max_row_length": 3,
        "ods_numeric_cell_count": 3,
        "ods_string_cell_count": 0,
        "ods_row_count": 1,
        "ods_empty_cell_count": 0,
        "ods_column_count": 3,
        "ods_empty_row_count": 0,
        "ods_has_merged_cells": False,
        "ods_numeric_density": 1.0,
        "ods_average_cells_per_row": 3.0,
        "ods_has_empty_rows": False,
        "ods_merged_cell_count": 0,
        "ods_avg_cells_per_sheet": 3.0,
        "ods_data_density": 1.0,
        "ods_max_cell_value_length": 3,
        "ods_min_cell_value_length": 3,
        "ods_all_sheets_have_data": True,
        "ods_is_single_sheet": True,
        "ods_string_density": 0.0,
        "ods_max_numeric_value": 3.0,
        "ods_has_string_cells": False,
        "ods_min_numeric_value": 1.0,
        "ods_has_numeric_cells": True,
        "ods_nonempty_row_count": 1,
        "ods_is_empty": False,
        "ods_is_single_row": True,
        "ods_avg_row_length": 3.0,
        "ods_nonempty_cell_count": 3,
        "ods_cell_value_variance": 0.6666666666666666,
        "ods_column_value_variance": 0.0,
        "ods_has_formulas": False,
        "ods_row_value_variance": 0.0,
        "ods_is_single_cell": False,
        "ods_is_rectangular": True,
        "ods_total_string_length": 0,
        "ods_is_all_numeric": True,
        "ods_empty_sheet_count": 0,
        "ods_numeric_sum": 6.0,
        "ods_min_row_length": 3,
        "ods_avg_numeric_value": 2.0,
        "ods_nonempty_row_ratio": 1.0,
        "ods_longest_row_index": 0,
        "ods_numeric_sum_all": 6.0,
        "ods_empty_column_count": 0,
        "ods_max_numeric_sum": 6.0,
        "ods_cell_density": 3.0,
        "ods_numeric_ratio": 1.0,
        "ods_is_square": False,
        "ods_numeric_column_count": 3,
        "ods_row_cell_variance": 0.0,
        "ods_string_cell_ratio": 0.0,
        "ods_widest_column_index": 0,
        "ods_numeric_cell_ratio": 1.0,
        "ods_column_fill_rate": 1.0,
        "ods_value_type_count": 1,
        "ods_nonempty_cell_percentage": 1.0,
    },
}

_SAMPLE_PATHS = {"minimal": MINIMAL, "single": SINGLE, "numeric": NUMERIC}

_ANALYTICS_CASES = [
    (sample_key, func_name)
    for sample_key, funcs in EXPECTED_ANALYTICS.items()
    for func_name in funcs
]


class TestAnalyticsFilePathBased:
    @pytest.mark.parametrize(
        "sample_key,func_name",
        _ANALYTICS_CASES,
        ids=[f"{fn}[{sk}]" for sk, fn in _ANALYTICS_CASES],
    )
    def test_function_matches_expected(self, sample_key, func_name):
        func = getattr(ods, func_name, None)
        if func is None:
            pytest.skip(f"{func_name} not exported from ods package")
        expected = EXPECTED_ANALYTICS[sample_key][func_name]
        actual = func(_SAMPLE_PATHS[sample_key])
        assert _close(actual, expected), f"{func_name}({sample_key}): {actual!r} != {expected!r}"

    def test_all_expected_functions_are_callable(self):
        missing = [name for name in EXPECTED_ANALYTICS["minimal"] if not callable(getattr(ods, name, None))]
        assert missing == []

    def test_expected_table_covers_at_least_70_functions(self):
        assert len(EXPECTED_ANALYTICS["minimal"]) >= 70


class TestAnalyticsIndexErrorEdgeCases:
    """Documents actual (unguarded) behavior for sheet_index out of range.

    Unlike their sibling functions, these four ods_analytics.py functions
    index doc.sheets[sheet_index] directly without a bounds check, so an
    out-of-range sheet_index raises IndexError rather than returning a
    default value. This is intentionally captured as regression coverage
    of current behavior.
    """

    @pytest.mark.parametrize(
        "func_name",
        ["ods_max_numeric_value", "ods_min_numeric_value", "ods_has_string_cells", "ods_has_numeric_cells"],
    )
    def test_out_of_range_sheet_index_raises_index_error(self, func_name):
        func = getattr(ods, func_name)
        with pytest.raises(IndexError):
            func(MINIMAL, sheet_index=99)

    def test_ods_max_numeric_value_within_range(self):
        assert ods.ods_max_numeric_value(MINIMAL, sheet_index=0) == 42.0

    def test_ods_min_numeric_value_within_range(self):
        assert ods.ods_min_numeric_value(MINIMAL, sheet_index=0) == 42.0

    def test_ods_has_string_cells_within_range(self):
        assert ods.ods_has_string_cells(MINIMAL, sheet_index=0) is True

    def test_ods_has_numeric_cells_within_range(self):
        assert ods.ods_has_numeric_cells(MINIMAL, sheet_index=0) is True


# ---------------------------------------------------------------------------
# models.py -- OdsModelDocument / OdsSheetModel / OdsCellModel
# ---------------------------------------------------------------------------


class TestModelsDocument:
    def test_from_file(self):
        doc = OdsModelDocument.from_file(MINIMAL)
        assert isinstance(doc, OdsModelDocument)

    def test_sheet_count(self):
        assert OdsModelDocument.from_file(MINIMAL).sheet_count == 1

    def test_sheet_names(self):
        assert OdsModelDocument.from_file(MINIMAL).sheet_names == ["Sheet1"]

    def test_path(self):
        assert OdsModelDocument.from_file(MINIMAL).path == MINIMAL

    def test_is_empty_false(self):
        assert OdsModelDocument.from_file(MINIMAL).is_empty is False

    def test_is_single_sheet(self):
        assert OdsModelDocument.from_file(MINIMAL).is_single_sheet is True

    def test_is_multi_sheet_false(self):
        assert OdsModelDocument.from_file(MINIMAL).is_multi_sheet is False

    def test_has_sheets(self):
        assert OdsModelDocument.from_file(MINIMAL).has_sheets is True

    def test_total_row_count(self):
        assert OdsModelDocument.from_file(MINIMAL).total_row_count == 2

    def test_max_sheet_rows(self):
        assert OdsModelDocument.from_file(MINIMAL).max_sheet_rows == 2

    def test_is_large_workbook_false(self):
        assert OdsModelDocument.from_file(MINIMAL).is_large_workbook is False

    def test_has_many_sheets_false(self):
        assert OdsModelDocument.from_file(MINIMAL).has_many_sheets is False

    def test_avg_rows_per_sheet(self):
        assert OdsModelDocument.from_file(MINIMAL).avg_rows_per_sheet == 2.0

    def test_is_uniform_sheet_size(self):
        assert OdsModelDocument.from_file(MINIMAL).is_uniform_sheet_size is True

    def test_min_sheet_rows(self):
        assert OdsModelDocument.from_file(MINIMAL).min_sheet_rows == 2

    def test_sheet_row_range(self):
        assert OdsModelDocument.from_file(MINIMAL).sheet_row_range == 0

    def test_has_data_sheets(self):
        assert OdsModelDocument.from_file(MINIMAL).has_data_sheets is True

    def test_largest_sheet_fraction(self):
        assert OdsModelDocument.from_file(MINIMAL).largest_sheet_fraction == 1.0

    def test_is_single_sheet_dominant(self):
        assert OdsModelDocument.from_file(MINIMAL).is_single_sheet_dominant is True

    def test_get_sheet_valid_index(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert isinstance(sheet, OdsSheetModel)

    def test_get_sheet_invalid_index(self):
        assert OdsModelDocument.from_file(MINIMAL).get_sheet(99) is None

    def test_sheets_returns_list_of_models(self):
        sheets = OdsModelDocument.from_file(MINIMAL).sheets()
        assert all(isinstance(s, OdsSheetModel) for s in sheets)

    def test_set_cell_value_mutates_document(self):
        doc = OdsModelDocument.from_file(MINIMAL)
        doc.set_cell_value(0, 0, 0, "EditedViaModel")
        assert doc.get_sheet(0).cell_at(0, 0).value == "EditedViaModel"

    def test_set_cell_value_out_of_range_raises(self):
        from ods.ods_parser import OdsError as ParserOdsError
        doc = OdsModelDocument.from_file(MINIMAL)
        with pytest.raises(ParserOdsError):
            doc.set_cell_value(99, 0, 0, "x")

    def test_save_to_file(self, tmp_path):
        doc = OdsModelDocument.from_file(MINIMAL)
        dest = tmp_path / "saved.ods"
        doc.save_to_file(dest)
        assert dest.exists()

    def test_save_to_file_empty_path_raises(self):
        from ods.ods_parser import OdsError as ParserOdsError
        doc = OdsModelDocument.from_file(MINIMAL)
        with pytest.raises(ParserOdsError):
            doc.save_to_file("")

    def test_to_dict(self):
        result = OdsModelDocument.from_file(MINIMAL).to_dict()
        assert result["sheet_count"] == 1
        assert result["sheet_names"] == ["Sheet1"]

    def test_repr(self):
        assert "OdsModelDocument" in repr(OdsModelDocument.from_file(MINIMAL))

    def test_ods_doc_alias(self):
        assert OdsDoc is OdsModelDocument

    def test_multi_sheet_properties(self):
        doc = OdsDocument(
            sheets=[
                OdsSheet(name="A", rows=[OdsRow(cells=[OdsCell(value=1)])] * 3),
                OdsSheet(name="B", rows=[OdsRow(cells=[OdsCell(value=1)])]),
            ]
        )
        model = OdsModelDocument(doc)
        assert model.is_multi_sheet is True
        assert model.min_sheet_rows == 1
        assert model.max_sheet_rows == 3
        assert model.sheet_row_range == 2
        assert model.is_uniform_sheet_size is False
        assert model.largest_sheet_fraction == pytest.approx(0.75)
        assert model.is_single_sheet_dominant is False


class TestModelsSheetAndCell:
    def test_sheet_name(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert sheet.name == "Sheet1"

    def test_sheet_row_count(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert sheet.row_count == 2

    def test_sheet_cells_iterator(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        cells = list(sheet.cells())
        assert len(cells) == 4
        assert all(isinstance(c, OdsCellModel) for c in cells)

    def test_sheet_cell_at_valid(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        cell = sheet.cell_at(1, 1)
        assert cell.value == 42.0

    def test_sheet_cell_at_invalid(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert sheet.cell_at(99, 99) is None

    def test_sheet_to_dict(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert sheet.to_dict() == {"name": "Sheet1", "row_count": 2}

    def test_sheet_repr(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        assert "OdsSheetModel" in repr(sheet)

    def test_cell_value_type_text(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        cell = sheet.cell_at(0, 0)
        assert cell.value == "Name"
        assert cell.value_type == "string"
        assert cell.text == "Name"

    def test_cell_to_dict(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        cell = sheet.cell_at(0, 0)
        assert cell.to_dict() == {"value": "Name", "value_type": "string", "text": "Name"}

    def test_cell_repr(self):
        sheet = OdsModelDocument.from_file(MINIMAL).get_sheet(0)
        cell = sheet.cell_at(0, 0)
        assert "OdsCellModel" in repr(cell)


# ---------------------------------------------------------------------------
# ods_workflow.py
# ---------------------------------------------------------------------------


class TestWorkflow:
    def test_minimal_workflow(self):
        result = ods_installed_workflow(MINIMAL)
        assert result == {"format": "ods", "loaded": True, "sheet_count": 1, "row_count": 2}

    def test_numeric_workflow(self):
        result = ods_installed_workflow(NUMERIC)
        assert result["loaded"] is True
        assert result["row_count"] == 1

    def test_truncated_workflow_not_loaded(self):
        result = ods_installed_workflow(TRUNCATED)
        assert result["format"] == "ods"
        assert result["loaded"] is False

    def test_accepts_path_object(self):
        result = ods_installed_workflow(Path(MINIMAL))
        assert result["loaded"] is True


# ---------------------------------------------------------------------------
# ods_sheet_iterator.py / ods_row_iterator.py
# ---------------------------------------------------------------------------


class TestSheetIterator:
    def test_yields_table_instances(self):
        sheets = list(ods_iter_sheets(MINIMAL))
        assert len(sheets) == 1
        assert all(isinstance(s, Table) for s in sheets)

    def test_sheet_name_and_qname(self):
        sheet = next(ods_iter_sheets(MINIMAL))
        assert sheet.name == "Sheet1"
        assert sheet.spec_qname == "table:table"

    def test_sheet_rows_accessible(self):
        sheet = next(ods_iter_sheets(MINIMAL))
        assert len(sheet.rows) == 2

    def test_truncated_yields_nothing(self):
        assert list(ods_iter_sheets(TRUNCATED)) == []

    def test_numeric_sample(self):
        sheets = list(ods_iter_sheets(NUMERIC))
        assert len(sheets) == 1
        assert len(sheets[0].rows) == 1


class TestRowIterator:
    def test_yields_table_row_instances(self):
        rows = list(ods_iter_rows(MINIMAL))
        assert len(rows) == 2
        assert all(isinstance(r, TableRow) for r in rows)

    def test_row_qname(self):
        row = next(ods_iter_rows(MINIMAL))
        assert row.spec_qname == "table:table-row"

    def test_row_cells_accessible(self):
        rows = list(ods_iter_rows(MINIMAL))
        assert len(rows[0].cells) == 2
        assert len(rows[1].cells) == 2

    def test_truncated_yields_nothing(self):
        assert list(ods_iter_rows(TRUNCATED)) == []

    def test_numeric_sample_single_row(self):
        rows = list(ods_iter_rows(NUMERIC))
        assert len(rows) == 1
        assert len(rows[0].cells) == 3


# ---------------------------------------------------------------------------
# spec/ shaped canonical classes
# ---------------------------------------------------------------------------


class TestSpecClasses:
    def test_table_qname_and_fact_ref(self):
        assert Table.spec_qname == "table:table"
        assert Table.spec_fact_ref == "SAL-ODS-01068"

    def test_table_properties(self):
        t = Table({"name": "S1", "rows": [1, 2, 3]})
        assert t.name == "S1"
        assert t.rows == [1, 2, 3]
        assert t.to_dict() == {"name": "S1", "rows": [1, 2, 3]}

    def test_table_defaults(self):
        t = Table({})
        assert t.name == ""
        assert t.rows == []

    def test_table_row_qname_and_fact_ref(self):
        assert TableRow.spec_qname == "table:table-row"
        assert TableRow.spec_fact_ref == "SAL-ODS-00001"

    def test_table_row_properties(self):
        tr = TableRow({"cells": ["a", "b"]})
        assert tr.cells == ["a", "b"]
        assert tr.to_dict() == {"cells": ["a", "b"]}

    def test_table_row_defaults(self):
        assert TableRow({}).cells == []

    def test_table_cell_qname_and_fact_ref(self):
        assert TableCell.spec_qname == "table:table-cell"
        assert TableCell.spec_fact_ref == "SAL-ODS-01069"

    def test_table_cell_properties(self):
        tc = TableCell({"value": "x", "value_type": "string", "col_span": 2})
        assert tc.value == "x"
        assert tc.value_type == "string"
        assert tc.col_span == 2

    def test_table_cell_defaults(self):
        tc = TableCell({})
        assert tc.value == ""
        assert tc.value_type == "string"
        assert tc.col_span == 1

    def test_document_qname_and_fact_ref(self):
        assert Document.spec_qname == "office:document"
        assert Document.spec_fact_ref == "SAL-ODS-00029"
        assert Document.facade_names == ["OdsDocument"]

    def test_document_properties(self):
        d = Document({"sheets": [{"name": "S1"}, {"name": "S2"}]})
        assert d.sheet_count == 2
        assert d.is_ods is True
        assert len(d.sheets) == 2

    def test_document_to_dict(self):
        d = Document({"sheets": []})
        assert d.to_dict() == {"sheets": []}

    def test_document_repr(self):
        d = Document({"sheets": []})
        assert "Document" in repr(d)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_parser_ods_error_is_exception(self):
        assert issubclass(OdsError, Exception)

    def test_invalid_container_error_subclass(self):
        assert issubclass(OdsInvalidContainerError, OdsError)

    def test_size_error_subclass(self):
        assert issubclass(OdsSizeError, OdsError)

    def test_exceptions_module_ods_error(self):
        assert issubclass(ExcOdsError, Exception)

    def test_exceptions_module_parse_error_subclass(self):
        assert issubclass(OdsParseError, ExcOdsError)

    def test_exceptions_module_write_error_subclass(self):
        assert issubclass(OdsWriteError, ExcOdsError)

    def test_csv_export_error_is_exception(self):
        assert issubclass(OdsCsvExportError, Exception)

    def test_package_level_ods_error_is_parser_variant(self):
        # ods_parser is imported after exceptions.py in __init__.py, so the
        # package-level OdsError resolves to ods_parser.OdsError.
        assert ods.OdsError is OdsError

    def test_can_raise_and_catch_invalid_container_error(self):
        with pytest.raises(OdsError):
            raise OdsInvalidContainerError("bad container")

    def test_can_raise_and_catch_size_error(self):
        with pytest.raises(OdsError):
            raise OdsSizeError("too big")

    def test_can_raise_and_catch_parse_error(self):
        with pytest.raises(ExcOdsError):
            raise OdsParseError("bad parse")

    def test_can_raise_and_catch_write_error(self):
        with pytest.raises(ExcOdsError):
            raise OdsWriteError("bad write")
