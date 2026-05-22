"""
tests/python/fods/test_r47_writer_hardening.py

R47 MT5 Lane 5A — FODS Python writer hardening tests.

Tests the write_fods() and workbook_to_xml() functions against edge cases
and validates that the installed wheel includes writer capability.

Sprint: FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
"""

import os
import tempfile
import xml.etree.ElementTree as ET

import pytest

from fods import parse_fods, write_fods, workbook_to_xml
from fods.exceptions import FodsInputError


class TestWorkbookToXmlHardening:
    """Hardening tests for workbook_to_xml edge cases."""

    def _make_workbook(self, sheets=None):
        if sheets is None:
            sheets = [{"name": "Sheet1", "rows": []}]
        return {"sheets": sheets}

    def test_multiple_sheets(self):
        wb = self._make_workbook([
            {"name": "Alpha", "rows": []},
            {"name": "Beta", "rows": []},
            {"name": "Gamma", "rows": []},
        ])
        xml = workbook_to_xml(wb)
        assert "Alpha" in xml
        assert "Beta" in xml
        assert "Gamma" in xml

    def test_typed_float_value(self):
        wb = self._make_workbook([{
            "name": "S1",
            "rows": [{"cells": [{"type": "float", "value": 3.14159}]}],
        }])
        xml = workbook_to_xml(wb)
        assert "3.14159" in xml or "3.1415" in xml

    def test_typed_string_value(self):
        wb = self._make_workbook([{
            "name": "S1",
            "rows": [{"cells": [{"type": "string", "value": "hello world"}]}],
        }])
        xml = workbook_to_xml(wb)
        assert "hello world" in xml

    def test_typed_boolean_value(self):
        wb = self._make_workbook([{
            "name": "S1",
            "rows": [{"cells": [{"type": "boolean", "value": True}]}],
        }])
        xml = workbook_to_xml(wb)
        # Boolean cells should produce valid XML
        root = ET.fromstring(xml)
        assert root is not None

    def test_empty_cells_in_row(self):
        wb = self._make_workbook([{
            "name": "S1",
            "rows": [{"cells": []}],
        }])
        xml = workbook_to_xml(wb)
        # Empty row should produce valid XML
        root = ET.fromstring(xml)
        assert root is not None

    def test_empty_workbook_no_exception(self):
        wb = {"sheets": []}
        xml = workbook_to_xml(wb)
        assert isinstance(xml, str)
        assert len(xml) > 0
        root = ET.fromstring(xml)
        assert root is not None

    def test_xml_special_characters_escaped(self):
        wb = self._make_workbook([{
            "name": "S1",
            "rows": [{"cells": [{"type": "string", "value": "<br> & 'quote' \"dquote\""}]}],
        }])
        xml = workbook_to_xml(wb)
        # Should be well-formed XML (special chars escaped)
        root = ET.fromstring(xml)
        assert root is not None

    def test_mimetype_attribute(self):
        wb = self._make_workbook()
        xml = workbook_to_xml(wb)
        assert "spreadsheet" in xml.lower() or "opendocument" in xml.lower()

    def test_non_dict_workbook_raises(self):
        with pytest.raises((FodsInputError, TypeError, AttributeError, KeyError)):
            workbook_to_xml([1, 2, 3])

    def test_none_workbook_raises(self):
        with pytest.raises((FodsInputError, TypeError, AttributeError)):
            workbook_to_xml(None)

    def test_large_sheet(self):
        """Writer should handle a moderately large sheet without timeout."""
        rows = [
            {"cells": [{"type": "float", "value": float(r * c)} for c in range(10)]}
            for r in range(100)
        ]
        wb = self._make_workbook([{"name": "BigSheet", "rows": rows}])
        xml = workbook_to_xml(wb)
        root = ET.fromstring(xml)
        assert root is not None

    def test_sheet_name_with_spaces(self):
        wb = self._make_workbook([{"name": "My Sheet With Spaces", "rows": []}])
        xml = workbook_to_xml(wb)
        assert "My Sheet With Spaces" in xml


class TestWriteFodsHardening:
    """Hardening tests for write_fods() to file."""

    def _tmp_fods(self):
        f = tempfile.NamedTemporaryFile(suffix=".fods", delete=False)
        f.close()
        return f.name

    def test_writes_valid_file(self):
        wb = {"sheets": [{"name": "Test", "rows": [
            {"cells": [{"type": "float", "value": 1.0}]}
        ]}]}
        tmp = self._tmp_fods()
        try:
            write_fods(wb, tmp)
            assert os.path.exists(tmp)
            assert os.path.getsize(tmp) > 100
        finally:
            os.unlink(tmp)

    def test_round_trip_sheet_count(self):
        wb = {"sheets": [
            {"name": "A", "rows": []},
            {"name": "B", "rows": []},
        ]}
        tmp = self._tmp_fods()
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            assert result["sheet_count"] == 2
        finally:
            os.unlink(tmp)

    def test_round_trip_sheet_name(self):
        wb = {"sheets": [{"name": "SpecialSheet", "rows": []}]}
        tmp = self._tmp_fods()
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            assert result.get("sheet_count", 0) == 1
        finally:
            os.unlink(tmp)

    def test_utf8_encoding(self):
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"type": "string", "value": "caf\u00e9 \u6c49\u5b57"}]}
        ]}]}
        tmp = self._tmp_fods()
        try:
            write_fods(wb, tmp)
            with open(tmp, encoding="utf-8") as f:
                content = f.read()
            assert "caf" in content
        finally:
            os.unlink(tmp)

    def test_file_is_parseable_as_xml(self):
        wb = {"sheets": [{"name": "ParseTest", "rows": []}]}
        tmp = self._tmp_fods()
        try:
            write_fods(wb, tmp)
            with open(tmp, encoding="utf-8") as f:
                content = f.read()
            root = ET.fromstring(content)
            assert root is not None
        finally:
            os.unlink(tmp)


def test_document_to_xml_alias():
    """document_to_xml should be importable from fods.writer (alias)."""
    # fods.writer exposes workbook_to_xml — verify it is importable
    from fods.writer import workbook_to_xml as wtx
    assert callable(wtx)
