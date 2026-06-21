"""TC-VAL-001: FODS spec-parity tests — verify parser handles ODF QName elements correctly.

These tests verify that the FODS parser correctly reads the canonical ODF spreadsheet
elements (table:table, table:table-row, table:table-cell, office:document, etc.)
and that the neutral model maps to the expected spec QName concepts.

Uses real FODS fixture files from samples/by-format/fods/.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))

from fods.parser import parse_fods
from fods.models import FodsDocument, FodsSheet, FodsCell


_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = _SAMPLES / "minimal-spreadsheet.fods"
_MULTI_SHEET = _SAMPLES / "multi-sheet-basic.fods"
_TYPED = _SAMPLES / "typed-values-basic.fods"


class TestParserReadsTableTableElement:
    """Verify sheet data comes from table:table elements."""

    def test_parser_reads_table_table_element(self):
        """Parser produces at least one sheet — sourced from table:table."""
        doc = FodsDocument.from_file(str(_MINIMAL))
        sheets = doc.sheets()
        assert len(sheets) >= 1, "Expected >= 1 sheet from table:table elements"

    def test_sheet_has_spec_qname(self):
        """FodsSheet class has spec_qname = table:table."""
        assert FodsSheet.spec_qname == "table:table"

    def test_multi_sheet_file_produces_multiple_tables(self):
        """Multi-sheet FODS file produces multiple FodsSheet objects."""
        doc = FodsDocument.from_file(str(_MULTI_SHEET))
        sheets = doc.sheets()
        assert len(sheets) >= 2, f"Expected >= 2 sheets, got {len(sheets)}"


class TestParserReadsTableTableRow:
    """Verify row data comes from table:table-row elements."""

    def test_parser_reads_table_table_row(self):
        """Sheet has rows — sourced from table:table-row elements."""
        doc = FodsDocument.from_file(str(_MINIMAL))
        sheets = doc.sheets()
        assert sheets, "No sheets found"
        sheet = sheets[0]
        assert sheet.row_count >= 1, "Expected >= 1 row from table:table-row elements"


class TestParserReadsTableTableCell:
    """Verify cell data comes from table:table-cell elements."""

    def test_parser_reads_table_table_cell(self):
        """Neutral model rows have cells — sourced from table:table-cell elements."""
        raw = parse_fods(str(_TYPED))
        sheet = raw["sheets"][0]
        rows = sheet.get("rows", [])
        assert rows, "No rows found in neutral model"
        # rows may be list-of-lists or list-of-dicts; in either case first row has cells
        first_row = rows[0]
        cells = first_row.get("cells", first_row) if isinstance(first_row, dict) else first_row
        assert len(cells) >= 1, "Expected >= 1 cell in first row"

    def test_cell_has_spec_qname(self):
        """FodsCell class has spec_qname = table:table-cell."""
        assert FodsCell.spec_qname == "table:table-cell"

    def test_neutral_model_cells_have_value_type(self):
        """Typed cells in neutral model have value_type key from table:table-cell attributes."""
        raw = parse_fods(str(_TYPED))
        sheet = raw["sheets"][0]
        rows = sheet.get("rows", [])
        all_cells = []
        for row in rows:
            row_cells = row.get("cells", row) if isinstance(row, dict) else row
            all_cells.extend(row_cells if isinstance(row_cells, list) else [])
        typed = [c for c in all_cells if isinstance(c, dict) and c.get("value_type")]
        assert typed, "Expected at least one cell with value_type in neutral model"


class TestWriterEmitsOdfNamespaces:
    """Verify writer emits ODF namespace declarations in output."""

    def test_writer_emits_correct_odf_namespaces(self, tmp_path):
        """FODS writer produces output with ODF namespace URIs."""
        from fods.writer import write_fods
        raw = parse_fods(str(_MINIMAL))
        out = tmp_path / "test-output.fods"
        write_fods(raw, str(out))
        content = out.read_text(encoding="utf-8")
        assert "urn:oasis:names:tc:opendocument" in content, (
            "FODS writer output missing ODF namespace URI"
        )
        assert "office:document" in content or "office:spreadsheet" in content, (
            "FODS writer output missing office: element"
        )


class TestNeutralModelHasExpectedEntities:
    """Verify neutral model has expected spec-mapped entities."""

    def test_neutral_model_has_expected_entities(self):
        """Neutral model from parse_fods() has workbook-level and sheet-level entities."""
        raw = parse_fods(str(_MINIMAL))
        assert isinstance(raw, dict), "parse_fods should return dict"
        assert "sheets" in raw, "Neutral model must have 'sheets' key (maps to table:table)"
        assert isinstance(raw["sheets"], list), "'sheets' must be a list"
        assert len(raw["sheets"]) >= 1, "Expected at least 1 sheet"

    def test_document_has_spec_qname(self):
        """FodsDocument class has spec_qname = office:document."""
        assert FodsDocument.spec_qname == "office:document"

    def test_sheet_rows_map_to_table_row_elements(self):
        """Sheet rows list maps to table:table-row elements."""
        raw = parse_fods(str(_MINIMAL))
        sheet = raw["sheets"][0]
        assert "rows" in sheet, "Sheet must have 'rows' key (maps to table:table-row)"
        assert isinstance(sheet["rows"], list)
