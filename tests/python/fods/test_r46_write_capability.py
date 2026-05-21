"""
R46 MT6: FODS Python write/export capability tests.

Tests that write_fods() and workbook_to_xml() correctly serialize
neutral model workbook dicts to valid FODS XML.
"""

import tempfile
from pathlib import Path

import pytest

from fods import write_fods, workbook_to_xml, parse_fods
from fods.exceptions import FodsInputError


def _minimal_workbook():
    return {
        "sheets": [
            {
                "name": "Sheet1",
                "rows": [
                    {"cells": [{"value_type": "string", "text_content": "Hello"}]},
                    {"cells": [{"value_type": "float", "value": 42.0}]},
                ]
            }
        ]
    }


class TestWorkbookToXml:
    def test_returns_string(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert isinstance(xml, str)

    def test_has_xml_declaration(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert xml.startswith("<?xml")

    def test_has_office_document_root(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "office:document" in xml

    def test_has_office_spreadsheet(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "office:spreadsheet" in xml

    def test_has_table_table(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "table:table" in xml

    def test_sheet_name_in_output(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "Sheet1" in xml

    def test_cell_text_content_in_output(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "Hello" in xml

    def test_numeric_value_in_output(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "42" in xml

    def test_raises_on_non_dict(self):
        with pytest.raises(FodsInputError):
            workbook_to_xml("not a dict")

    def test_empty_workbook_valid_xml(self):
        xml = workbook_to_xml({"sheets": []})
        assert "office:document" in xml

    def test_mimetype_in_output(self):
        xml = workbook_to_xml(_minimal_workbook())
        assert "vnd.oasis.opendocument.spreadsheet" in xml


class TestWriteFods:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "test.fods"
        write_fods(_minimal_workbook(), out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_written_file_is_utf8(self, tmp_path):
        out = tmp_path / "test.fods"
        write_fods(_minimal_workbook(), out)
        content = out.read_text(encoding="utf-8")
        assert "Hello" in content

    def test_round_trip_parse_written_file(self, tmp_path):
        """Write a workbook, then parse it back — must not error."""
        out = tmp_path / "round-trip.fods"
        write_fods(_minimal_workbook(), out)
        result = parse_fods(str(out))
        # parse_fods returns error dict on failure (never raises)
        assert result.get("error") is None, f"Parse error: {result.get('error')}"
        assert result["sheet_count"] == 1

    def test_round_trip_preserves_sheet_name(self, tmp_path):
        """Sheet name must be preserved through write-parse round-trip."""
        wb = {"sheets": [{"name": "MySheet", "rows": []}]}
        out = tmp_path / "rt.fods"
        write_fods(wb, out)
        result = parse_fods(str(out))
        sheet_names = [s["name"] for s in result.get("sheets", [])]
        assert "MySheet" in sheet_names

    def test_multiple_sheets(self, tmp_path):
        """Multiple sheets are written and preserved."""
        wb = {
            "sheets": [
                {"name": "Alpha", "rows": []},
                {"name": "Beta", "rows": []},
            ]
        }
        out = tmp_path / "multi.fods"
        write_fods(wb, out)
        result = parse_fods(str(out))
        assert result["sheet_count"] == 2
