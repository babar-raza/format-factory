"""
test_rnext_fods_workbook_to_xml.py -- Dedicated test coverage for workbook_to_xml.

Gap: GAP-FODS-FOSS-WORKBOOK_TO_-001 (missing_test_coverage)
Tests: basic serialization, round-trip, empty workbook, multi-sheet, cell values, error handling.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.writer import workbook_to_xml
from fods.exceptions import FodsInputError


def _wb(sheets=None):
    """Create a minimal FODS workbook dict."""
    return {"sheets": sheets or []}


def _sheet(name="Sheet1", rows=None):
    return {"name": name, "rows": rows or []}


def _row(cells=None):
    return {"cells": cells or []}


def _cell(value="", value_type="string"):
    return {"value": value, "value_type": value_type}


class TestWorkbookToXmlBasic:
    def test_returns_string(self):
        xml = workbook_to_xml(_wb())
        assert isinstance(xml, str)

    def test_xml_declaration_present(self):
        xml = workbook_to_xml(_wb())
        assert xml.startswith("<?xml")

    def test_contains_office_spreadsheet_tag(self):
        xml = workbook_to_xml(_wb())
        assert "office:spreadsheet" in xml

    def test_empty_workbook_valid_xml(self):
        xml = workbook_to_xml(_wb())
        assert "office:document" in xml

    def test_single_sheet_name_in_output(self):
        xml = workbook_to_xml(_wb([_sheet("MySheet")]))
        assert "MySheet" in xml

    def test_multi_sheet_names(self):
        wb = _wb([_sheet("A"), _sheet("B"), _sheet("C")])
        xml = workbook_to_xml(wb)
        assert "A" in xml
        assert "B" in xml
        assert "C" in xml

    def test_cell_value_in_output(self):
        sheet = _sheet("S1", [_row([_cell("hello")])])
        xml = workbook_to_xml(_wb([sheet]))
        assert "hello" in xml

    def test_numeric_cell_type(self):
        sheet = _sheet("S1", [_row([_cell("42", "float")])])
        xml = workbook_to_xml(_wb([sheet]))
        assert "42" in xml


class TestWorkbookToXmlRoundTrip:
    def test_parse_written_xml(self):
        from fods.parser import parse_fods_strict
        sheet = _sheet("Test", [_row([_cell("data")])])
        xml = workbook_to_xml(_wb([sheet]))
        tmp = Path(__file__).parent / "_tmp_fods_roundtrip.fods"
        try:
            tmp.write_text(xml, encoding="utf-8")
            wb2 = parse_fods_strict(str(tmp))
            assert wb2["sheet_count"] >= 1
        finally:
            tmp.unlink(missing_ok=True)


class TestWorkbookToXmlErrors:
    def test_not_dict_raises(self):
        with pytest.raises((FodsInputError, TypeError)):
            workbook_to_xml("not a dict")

    def test_none_raises(self):
        with pytest.raises((FodsInputError, TypeError)):
            workbook_to_xml(None)

    def test_missing_sheets_key_still_works(self):
        xml = workbook_to_xml({})
        assert isinstance(xml, str)
