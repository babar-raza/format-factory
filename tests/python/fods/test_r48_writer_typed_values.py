"""
tests/python/fods/test_r48_writer_typed_values.py

R48 Lane 3A — FODS writer typed-value semantic repair tests.

Verifies that typed values (float, boolean, string) are correctly serialized
to FODS XML with the correct office:value-type attributes, using BOTH the
canonical `value_type` field AND the legacy `type` alias.

Closes the R47 defect: R47 hardening tests used `"type"` key but writer only
read `"value_type"` — float cells silently serialized as string.

Sprint: FORMAT-FACTORY-R48-ARTIFACT-RC-CLEAN-CLOSEOUT-AND-PHASE-AUDIT-COMPLETION-001
"""

import xml.etree.ElementTree as ET


from fods import parse_fods, workbook_to_xml, write_fods
import tempfile
from pathlib import Path

# ODF namespace URIs
_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _make_single_cell_wb(cell_dict: dict, sheet_name: str = "S1") -> dict:
    return {"sheets": [{"name": sheet_name, "rows": [{"cells": [cell_dict]}]}]}


def _get_cells(xml_str: str) -> list[ET.Element]:
    """Return all table:table-cell elements from the XML."""
    root = ET.fromstring(xml_str)
    return root.findall(f".//{{{_NS_TABLE}}}table-cell")


class TestCanonicalValueType:
    """Tests using canonical `value_type` field (matches parser output schema)."""

    def test_float_with_value_type_has_correct_office_attribute(self):
        """Float cell with value_type='float' must emit office:value-type='float'."""
        wb = _make_single_cell_wb({"value_type": "float", "value": 3.14})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert len(cells) == 1
        vt = cells[0].get(f"{{{_NS_OFFICE}}}value-type")
        assert vt == "float", f"Expected office:value-type='float', got {vt!r}"

    def test_float_with_value_type_has_office_value_attribute(self):
        """Float cell must emit office:value attribute with numeric string."""
        wb = _make_single_cell_wb({"value_type": "float", "value": 42.5})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        val = cells[0].get(f"{{{_NS_OFFICE}}}value")
        assert val == "42.5", f"Expected office:value='42.5', got {val!r}"

    def test_boolean_true_with_value_type(self):
        """Boolean True cell must emit office:value-type='boolean' + boolean-value='true'."""
        wb = _make_single_cell_wb({"value_type": "boolean", "value": True})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}value-type") == "boolean"
        assert cells[0].get(f"{{{_NS_OFFICE}}}boolean-value") == "true"

    def test_boolean_false_with_value_type(self):
        """Boolean False cell must emit boolean-value='false'."""
        wb = _make_single_cell_wb({"value_type": "boolean", "value": False})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}boolean-value") == "false"

    def test_string_with_value_type(self):
        """String cell must emit office:value-type='string'."""
        wb = _make_single_cell_wb({"value_type": "string", "value": "hello"})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}value-type") == "string"


class TestLegacyTypeAlias:
    """Tests using legacy `type` field — the R47 defect pattern, now fixed."""

    def test_float_via_legacy_type_has_office_float_attribute(self):
        """R47 defect fix: float cell with `type` key must still emit office:value-type='float'."""
        wb = _make_single_cell_wb({"type": "float", "value": 3.14})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        vt = cells[0].get(f"{{{_NS_OFFICE}}}value-type")
        assert vt == "float", (
            f"R47 defect: `type` alias not accepted by writer. "
            f"Got office:value-type={vt!r} (expected 'float')"
        )

    def test_float_via_legacy_type_has_office_value(self):
        """R47 defect fix: float cell with `type` alias must emit office:value."""
        wb = _make_single_cell_wb({"type": "float", "value": 99.0})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        val = cells[0].get(f"{{{_NS_OFFICE}}}value")
        assert val == "99.0", f"Expected '99.0', got {val!r}"

    def test_boolean_via_legacy_type(self):
        """Boolean cell with `type` alias must emit office:value-type='boolean'."""
        wb = _make_single_cell_wb({"type": "boolean", "value": True})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}value-type") == "boolean"

    def test_string_via_legacy_type(self):
        """String cell with `type` alias must emit office:value-type='string'."""
        wb = _make_single_cell_wb({"type": "string", "value": "world"})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}value-type") == "string"

    def test_value_type_takes_precedence_over_type(self):
        """When both `value_type` and `type` present, `value_type` wins."""
        wb = _make_single_cell_wb({"value_type": "float", "type": "string", "value": 1.0})
        xml = workbook_to_xml(wb)
        cells = _get_cells(xml)
        assert cells[0].get(f"{{{_NS_OFFICE}}}value-type") == "float"


class TestTypedValueRoundTrip:
    """Round-trip tests: write typed cell, parse back, verify value_type preserved."""

    def test_float_roundtrip_via_canonical(self):
        """Float written with value_type must be read back as value_type='float'."""
        wb = _make_single_cell_wb({"value_type": "float", "value": 2.718})
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            sheets = result["sheets"]
            assert len(sheets) == 1
            rows = sheets[0]["rows"]
            assert len(rows) == 1
            cells = rows[0]["cells"]
            assert len(cells) == 1
            cell = cells[0]
            assert cell.get("value_type") == "float", (
                f"Round-trip: expected value_type='float', got {cell.get('value_type')!r}"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_float_roundtrip_via_legacy_type(self):
        """Float written via `type` alias must be read back as value_type='float'."""
        wb = _make_single_cell_wb({"type": "float", "value": 1.23})
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            cell = result["sheets"][0]["rows"][0]["cells"][0]
            assert cell.get("value_type") == "float", (
                f"Round-trip via legacy `type`: expected value_type='float', "
                f"got {cell.get('value_type')!r}"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_boolean_roundtrip(self):
        """Boolean True round-trips with value_type='boolean'."""
        wb = _make_single_cell_wb({"value_type": "boolean", "value": True})
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            cell = result["sheets"][0]["rows"][0]["cells"][0]
            assert cell.get("value_type") == "boolean"
        finally:
            tmp.unlink(missing_ok=True)
