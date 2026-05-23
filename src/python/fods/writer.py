"""
writer.py -- FODS serializer for format-factory-fods.

Writes a neutral model workbook dict to a FODS (Flat OpenDocument Spreadsheet)
XML file.

Public API:
  write_fods(workbook, file_path)  -- serialize workbook to FODS file
  workbook_to_xml(workbook)        -- serialize workbook to XML string

R46 MT6: Two-product capability deepening. Adds write/export path to FOSS package.

R53 MT6 (TC-0054): Formula preservation — writer emits table:formula attribute
verbatim when present in neutral model cell dict (key: ``formula``).  Cells
with formula attributes retain their display value via office:value/text:p.

R55 TC-0055 (style metadata): Writer re-emits ``office:automatic-styles`` and
``office:styles`` sections when present as ``_auto_styles_elem`` / ``_styles_elem``
in the workbook dict. Both sections are inserted before ``office:body``.

R55 TC-0056 (column definitions): Writer emits ``table:table-column`` elements
before row data when ``column_defs`` list is present in a sheet dict.  Each
column def dict maps directly from captured attributes (verbatim round-trip).

Capability level: alpha-foss-preview (write subset — cells with text, numeric
values, and formulas; style metadata (round-trip only); column definitions
(round-trip only)).

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION
from .exceptions import FodsInputError

# ODF 1.3 namespace URIs
_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
    "of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
}

_MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet-flat-xml"

# Register namespaces so ET uses the short prefixes
for _prefix, _uri in _NS.items():
    ET.register_namespace(_prefix, _uri)


def _qn(ns_prefix: str, local: str) -> str:
    return f"{{{_NS[ns_prefix]}}}{local}"


def _write_cell(parent: ET.Element, cell: dict[str, Any]) -> None:
    """Append a table:table-cell element for the given neutral model cell.

    Accepts both canonical ``value_type`` (matching parser output) and legacy
    ``type`` alias.  If both are present, ``value_type`` takes precedence.

    R48: fixed schema mismatch — R47 hardening tests used ``type`` but writer
    only read ``value_type``, causing float cells to silently serialize as string.
    """
    # Accept "type" as legacy alias; "value_type" is canonical (matches parser output)
    value_type = cell.get("value_type") or cell.get("type") or "string"
    raw_value = cell.get("value")
    text_content = cell.get("text_content", "")

    cell_el = ET.SubElement(parent, _qn("table", "table-cell"))

    # TC-0054: formula preservation — emit formula attribute verbatim if present.
    # Parser captures table:formula as-is (IR-FODS-008); writer must round-trip it.
    formula = cell.get("formula")
    if formula is not None:
        cell_el.set(_qn("table", "formula"), formula)

    if value_type == "float" and raw_value is not None:
        cell_el.set(_qn("office", "value-type"), "float")
        cell_el.set(_qn("office", "value"), str(raw_value))
        text_p = ET.SubElement(cell_el, _qn("text", "p"))
        text_p.text = str(raw_value)
    elif value_type == "boolean" and raw_value is not None:
        cell_el.set(_qn("office", "value-type"), "boolean")
        cell_el.set(_qn("office", "boolean-value"), "true" if raw_value else "false")
        text_p = ET.SubElement(cell_el, _qn("text", "p"))
        text_p.text = text_content or ("true" if raw_value else "false")
    else:
        # Default: string
        cell_el.set(_qn("office", "value-type"), "string")
        display = text_content or (str(raw_value) if raw_value is not None else "")
        if display:
            cell_el.set(_qn("office", "string-value"), display)
            text_p = ET.SubElement(cell_el, _qn("text", "p"))
            text_p.text = display


def _write_sheet(parent: ET.Element, sheet: dict[str, Any]) -> None:
    """Append a table:table element for the given neutral model sheet.

    R55 TC-0056: emits ``table:table-column`` elements before row data when
    ``column_defs`` list is present in the sheet dict.
    """
    table_el = ET.SubElement(parent, _qn("table", "table"))
    name = sheet.get("name", "Sheet1")
    table_el.set(_qn("table", "name"), name)

    # TC-0056: emit column definitions verbatim (round-trip)
    for col_def in sheet.get("column_defs", []):
        col_el = ET.SubElement(table_el, _qn("table", "table-column"))
        for attr_key, attr_val in col_def.items():
            col_el.set(attr_key, str(attr_val))

    rows = sheet.get("rows", [])
    for row in rows:
        row_el = ET.SubElement(table_el, _qn("table", "table-row"))
        cells = row.get("cells", [])
        for cell in cells:
            _write_cell(row_el, cell)


def workbook_to_xml(workbook: dict[str, Any]) -> str:
    """Serialize a neutral model workbook dict to a FODS XML string.

    Args:
        workbook: dict following the fods neutral model schema.
                  Required keys: sheets (list of sheet dicts).
                  Optional keys: odf_version_attr.

    Returns:
        UTF-8 XML string (str) representing a valid FODS document.
    """
    if not isinstance(workbook, dict):
        raise FodsInputError("workbook must be a dict")

    sheets = workbook.get("sheets", [])
    if not isinstance(sheets, list):
        raise FodsInputError("workbook['sheets'] must be a list")

    version = workbook.get("odf_version_attr", "1.3")

    # Build root element
    doc_el = ET.Element(_qn("office", "document"))
    doc_el.set(_qn("office", "version"), version)
    doc_el.set(_qn("office", "mimetype"), _MIMETYPE)

    # TC-0055: re-emit automatic-styles and styles before office:body
    auto_styles_elem = workbook.get("_auto_styles_elem")
    styles_elem = workbook.get("_styles_elem")
    if auto_styles_elem is not None:
        doc_el.append(auto_styles_elem)
    if styles_elem is not None:
        doc_el.append(styles_elem)

    # office:body > office:spreadsheet
    body_el = ET.SubElement(doc_el, _qn("office", "body"))
    spreadsheet_el = ET.SubElement(body_el, _qn("office", "spreadsheet"))

    for sheet in sheets:
        _write_sheet(spreadsheet_el, sheet)

    # Serialize
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body = ET.tostring(doc_el, encoding="unicode", xml_declaration=False)
    return xml_declaration + body


def write_fods(workbook: dict[str, Any], file_path: str | Path) -> None:
    """Write a neutral model workbook dict to a FODS file.

    Args:
        workbook: dict following the fods neutral model schema.
        file_path: destination path for the .fods file.
    """
    xml_content = workbook_to_xml(workbook)
    path = Path(file_path)
    path.write_text(xml_content, encoding="utf-8", newline="\n")
