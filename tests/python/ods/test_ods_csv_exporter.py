"""Tests for ODS CSV exporter — R33 deepening deliverable."""

import sys
import tempfile
from pathlib import Path

import pytest

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ods.ods_parser import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    parse_ods_strict,
)
from ods.ods_csv_exporter import (
    export_ods_to_csv,
    export_ods_to_csv_file,
    get_csv_export_capabilities,
    OdsCsvExportError,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc(sheets: list[OdsSheet]) -> OdsDocument:
    return OdsDocument(sheets=sheets, path="test.ods")


def _make_sheet(name: str, rows: list[list[tuple]]) -> OdsSheet:
    """Create a sheet from list of rows, each row is list of (value, vtype, text) tuples."""
    sheet_rows = []
    for row_data in rows:
        cells = [OdsCell(value=v, value_type=vt, text=t) for v, vt, t in row_data]
        sheet_rows.append(OdsRow(cells=cells))
    return OdsSheet(name=name, rows=sheet_rows)


# ---------------------------------------------------------------------------
# 1. Basic export
# ---------------------------------------------------------------------------

class TestCsvExportBasic:

    def test_single_cell(self):
        sheet = _make_sheet("Sheet1", [[("hello", "string", "hello")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "hello\r\n"

    def test_multiple_cells(self):
        sheet = _make_sheet("Sheet1", [
            [("a", "string", "a"), ("b", "string", "b"), ("c", "string", "c")]
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "a,b,c\r\n"

    def test_multiple_rows(self):
        sheet = _make_sheet("Sheet1", [
            [("r1c1", "string", "r1c1"), ("r1c2", "string", "r1c2")],
            [("r2c1", "string", "r2c1"), ("r2c2", "string", "r2c2")],
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "r1c1,r1c2\r\nr2c1,r2c2\r\n"

    def test_empty_sheet(self):
        sheet = _make_sheet("Sheet1", [])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == ""


# ---------------------------------------------------------------------------
# 2. Typed values
# ---------------------------------------------------------------------------

class TestCsvExportTypes:

    def test_float_value(self):
        sheet = _make_sheet("Sheet1", [[(42.5, "float", "42.5")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "42.5\r\n"

    def test_integer_float(self):
        """Float values that are integers should not have .0 suffix."""
        sheet = _make_sheet("Sheet1", [[(100.0, "float", "100")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "100\r\n"

    def test_date_value(self):
        sheet = _make_sheet("Sheet1", [[("2026-05-19", "date", "2026-05-19")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "2026-05-19\r\n"

    def test_boolean_value(self):
        sheet = _make_sheet("Sheet1", [[("true", "boolean", "true")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "true\r\n"

    def test_none_value(self):
        sheet = _make_sheet("Sheet1", [[(None, "", "")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc, include_empty_rows=True)
        assert csv == "\r\n"


# ---------------------------------------------------------------------------
# 3. RFC 4180 quoting
# ---------------------------------------------------------------------------

class TestCsvRfc4180:

    def test_comma_in_value(self):
        sheet = _make_sheet("Sheet1", [[("a,b", "string", "a,b")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == '"a,b"\r\n'

    def test_double_quotes_in_value(self):
        sheet = _make_sheet("Sheet1", [[('say "hi"', "string", 'say "hi"')]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == '"say ""hi"""\r\n'

    def test_newline_in_value(self):
        sheet = _make_sheet("Sheet1", [[("line1\nline2", "string", "line1\nline2")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == '"line1\nline2"\r\n'

    def test_no_quoting_for_plain(self):
        sheet = _make_sheet("Sheet1", [[("plain", "string", "plain")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "plain\r\n"


# ---------------------------------------------------------------------------
# 4. Trailing cell / row trimming
# ---------------------------------------------------------------------------

class TestCsvTrimming:

    def test_trailing_empty_cells_trimmed(self):
        sheet = _make_sheet("Sheet1", [
            [("data", "string", "data"), (None, "", ""), (None, "", "")]
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "data\r\n"

    def test_empty_rows_excluded_by_default(self):
        sheet = _make_sheet("Sheet1", [
            [("data", "string", "data")],
            [(None, "", "")],
            [("more", "string", "more")],
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv == "data\r\nmore\r\n"

    def test_empty_rows_included_when_requested(self):
        sheet = _make_sheet("Sheet1", [
            [("data", "string", "data")],
            [(None, "", "")],
            [("more", "string", "more")],
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc, include_empty_rows=True)
        assert csv == "data\r\n\r\nmore\r\n"


# ---------------------------------------------------------------------------
# 5. Sheet selection
# ---------------------------------------------------------------------------

class TestCsvSheetSelection:

    def test_second_sheet(self):
        s1 = _make_sheet("Sheet1", [[("s1", "string", "s1")]])
        s2 = _make_sheet("Sheet2", [[("s2", "string", "s2")]])
        doc = _make_doc([s1, s2])
        csv = export_ods_to_csv(doc, sheet_index=1)
        assert csv == "s2\r\n"

    def test_invalid_sheet_index(self):
        doc = _make_doc([_make_sheet("Sheet1", [])])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc, sheet_index=5)

    def test_negative_sheet_index(self):
        doc = _make_doc([_make_sheet("Sheet1", [])])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc, sheet_index=-1)

    def test_no_sheets(self):
        doc = _make_doc([])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc)


# ---------------------------------------------------------------------------
# 6. File output
# ---------------------------------------------------------------------------

class TestCsvFileOutput:

    def test_write_csv_file(self):
        sheet = _make_sheet("Sheet1", [
            [("a", "string", "a"), ("b", "string", "b")],
            [("c", "string", "c"), ("d", "string", "d")],
        ])
        doc = _make_doc([sheet])
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.csv"
            result_path = export_ods_to_csv_file(doc, out_path)
            assert Path(result_path).exists()
            content = Path(result_path).read_bytes().decode("utf-8")
            assert content == "a,b\r\nc,d\r\n"


# ---------------------------------------------------------------------------
# 7. Corpus integration
# ---------------------------------------------------------------------------

class TestCsvCorpusExport:

    def test_export_minimal_spreadsheet(self):
        sample = SAMPLES / "valid" / "minimal-spreadsheet.ods"
        if not sample.exists():
            pytest.skip("minimal-spreadsheet.ods not found")
        doc = parse_ods_strict(sample)
        csv = export_ods_to_csv(doc)
        assert len(csv) > 0
        assert "\r\n" in csv

    def test_export_numeric_row(self):
        sample = SAMPLES / "valid" / "numeric-row.ods"
        if not sample.exists():
            pytest.skip("numeric-row.ods not found")
        doc = parse_ods_strict(sample)
        csv = export_ods_to_csv(doc)
        assert len(csv) > 0

    def test_export_all_valid_samples(self):
        valid_dir = SAMPLES / "valid"
        if not valid_dir.exists():
            pytest.skip("valid samples dir not found")
        for ods_file in valid_dir.glob("*.ods"):
            doc = parse_ods_strict(ods_file)
            csv = export_ods_to_csv(doc)
            assert isinstance(csv, str), f"export failed for {ods_file.name}"


# ---------------------------------------------------------------------------
# 8. Capabilities
# ---------------------------------------------------------------------------

class TestCsvCapabilities:

    def test_capabilities_structure(self):
        caps = get_csv_export_capabilities()
        assert caps["format"] == "ods"
        assert caps["export_target"] == "csv"
        assert caps["rfc"] == "RFC 4180"
        assert "single_sheet_export" in caps["features"]
        assert caps["max_rows"] > 0
        assert caps["max_cols"] > 0


# ---------------------------------------------------------------------------
# 9. R35 Export Hardening
# ---------------------------------------------------------------------------

class TestR35ExportHardening:
    """R35 Lane E: deterministic output, Unicode, edge cases."""

    def test_deterministic_output(self):
        """Same input produces identical CSV on repeated calls."""
        sheet = _make_sheet("S", [[("a", "string", "a"), ("b", "string", "b")]])
        doc = _make_doc([sheet])
        csv1 = export_ods_to_csv(doc)
        csv2 = export_ods_to_csv(doc)
        assert csv1 == csv2

    def test_unicode_cell_values(self):
        """Unicode characters export correctly."""
        sheet = _make_sheet("S", [
            [("café", "string", "café"), ("naïve", "string", "naïve")],
            [("日本語", "string", "日本語"), ("中文", "string", "中文")],
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert "café" in csv
        assert "日本語" in csv

    def test_emoji_in_cell(self):
        """Emoji characters survive export."""
        sheet = _make_sheet("S", [[("hello 🌍", "string", "hello 🌍")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert "🌍" in csv

    def test_lf_line_ending(self):
        """LF-only line ending when requested."""
        sheet = _make_sheet("S", [
            [("a", "string", "a")],
            [("b", "string", "b")],
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc, line_ending="\n")
        assert "\r\n" not in csv
        assert csv == "a\nb\n"

    def test_include_empty_rows_preserves_blanks(self):
        """include_empty_rows=True preserves blank lines."""
        sheet = OdsSheet(name="s1", rows=[
            OdsRow(cells=[OdsCell(value="a", text="a", value_type="string")]),
            OdsRow(cells=[]),
            OdsRow(cells=[OdsCell(value="b", text="b", value_type="string")]),
        ])
        doc = OdsDocument(sheets=[sheet], path="")
        csv_with = export_ods_to_csv(doc, include_empty_rows=True)
        csv_without = export_ods_to_csv(doc, include_empty_rows=False)
        assert csv_with.count("\r\n") == 3
        assert csv_without.count("\r\n") == 2

    def test_cr_in_field_is_quoted(self):
        """Carriage return in field triggers RFC 4180 quoting."""
        sheet = _make_sheet("S", [[("a\rb", "string", "a\rb")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv.startswith('"')

    def test_comma_and_quotes_combined(self):
        """Field with both comma and quotes gets proper escaping."""
        sheet = _make_sheet("S", [[('"a",b', "string", '"a",b')]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert '"""a"",b"' in csv

    def test_large_float_precision(self):
        """Large floats export without scientific notation issues."""
        sheet = _make_sheet("S", [[(1234567890.12, "float", "1234567890.12")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert "1234567890.12" in csv


class TestR36ExportEdgeCases:
    """R36 deepening: multi-sheet selection and boundary conditions."""

    def test_sheet_index_out_of_range_raises(self):
        """Out-of-range sheet_index raises OdsCsvExportError."""
        sheet = _make_sheet("S1", [[("a", "string", "a")]])
        doc = _make_doc([sheet])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc, sheet_index=5)

    def test_negative_sheet_index_raises(self):
        """Negative sheet_index raises OdsCsvExportError."""
        sheet = _make_sheet("S1", [[("a", "string", "a")]])
        doc = _make_doc([sheet])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc, sheet_index=-1)

    def test_empty_document_raises(self):
        """Document with no sheets raises OdsCsvExportError."""
        doc = _make_doc([])
        with pytest.raises(OdsCsvExportError):
            export_ods_to_csv(doc)

    def test_multi_sheet_selects_correct_sheet(self):
        """sheet_index=1 selects second sheet, not first."""
        s1 = _make_sheet("First", [[("A", "string", "A")]])
        s2 = _make_sheet("Second", [[("B", "string", "B")]])
        doc = _make_doc([s1, s2])
        csv = export_ods_to_csv(doc, sheet_index=1)
        assert "B" in csv
        assert "A" not in csv

    def test_integer_float_renders_without_decimal(self):
        """Float value 42.0 renders as '42' not '42.0'."""
        sheet = _make_sheet("S", [[(42.0, "float", "42.0")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert "42\r\n" in csv or csv.strip() == "42"

    def test_none_cell_renders_as_empty(self):
        """Cell with None value renders as empty field."""
        sheet = _make_sheet("S", [[(None, "", "")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv.strip() == ""

    def test_file_export_creates_valid_file(self):
        """export_ods_to_csv_file creates a readable CSV file."""
        sheet = _make_sheet("S", [[("hello", "string", "hello")]])
        doc = _make_doc([sheet])
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            path = f.name
        try:
            export_ods_to_csv_file(doc, path)
            content = Path(path).read_text(encoding="utf-8")
            assert "hello" in content
        finally:
            Path(path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# 11. R37 RFC 4180 Compliance Deepening
# ---------------------------------------------------------------------------

class TestR37Rfc4180Compliance:
    """R37 deepening: RFC 4180 compliance edge cases."""

    def test_tab_character_not_quoted(self):
        """Tab characters do not trigger quoting (only comma/quote/newline do)."""
        sheet = _make_sheet("S", [[("a\tb", "string", "a\tb")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv.strip() == "a\tb"

    def test_semicolon_not_quoted(self):
        """Semicolons do not trigger quoting in RFC 4180."""
        sheet = _make_sheet("S", [[("a;b", "string", "a;b")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv.strip() == "a;b"

    def test_empty_string_cell_in_middle(self):
        """Empty string cell between non-empty cells exports as empty field."""
        sheet = _make_sheet("S", [
            [("a", "string", "a"), ("", "string", ""), ("c", "string", "c")]
        ])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert csv.strip() == "a,,c"

    def test_newline_in_field_quoted(self):
        """Newline in cell value triggers RFC 4180 quoting."""
        sheet = _make_sheet("S", [[("line1\nline2", "string", "line1\nline2")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert '"line1\nline2"' in csv

    def test_only_quotes_in_field(self):
        """Field containing only double-quotes is properly escaped."""
        sheet = _make_sheet("S", [[('"', "string", '"')]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert '""""' in csv

    def test_boolean_true_renders_as_text(self):
        """Boolean True cell renders as string representation."""
        sheet = _make_sheet("S", [[("true", "boolean", "true")]])
        doc = _make_doc([sheet])
        csv = export_ods_to_csv(doc)
        assert "true" in csv
