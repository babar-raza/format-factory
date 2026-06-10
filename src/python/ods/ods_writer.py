"""
ods_writer.py — ODS writer for format-factory-ods.

Public API:
  write_ods(doc, path)          — serialize OdsDocument to ODS file
  document_to_ods_bytes(doc)    — serialize OdsDocument to bytes (ZIP in memory)

Creates minimal valid ODS containers (mimetype + manifest + content.xml).
Technology: Python zipfile + xml.etree.ElementTree (stdlib, XXE-safe).

License: Apache-2.0
"""

from __future__ import annotations

import io
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, NS, ODS_MIMETYPE


_MANIFEST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
                   manifest:version="1.2">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"
                       manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
</manifest:manifest>
"""


def _cell_to_xml(cell: OdsCell) -> ET.Element:
    """Convert an OdsCell to a table:table-cell element."""
    el = ET.Element(f"{{{NS['table']}}}table-cell")
    if cell.value is None and not cell.text:
        return el
    vtype = cell.value_type or "string"
    el.set(f"{{{NS['office']}}}value-type", vtype)
    if vtype == "float" and cell.value is not None:
        el.set(f"{{{NS['office']}}}value", str(cell.value))
    elif vtype == "date" and cell.value is not None:
        el.set(f"{{{NS['office']}}}date-value", str(cell.value))
    elif vtype == "boolean" and cell.value is not None:
        el.set(f"{{{NS['office']}}}boolean-value", str(cell.value).lower())
    text_val = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
    if text_val:
        p = ET.SubElement(el, f"{{{NS['text']}}}p")
        p.text = text_val
    return el


def _build_content_xml(doc: OdsDocument) -> bytes:
    """Build content.xml bytes from an OdsDocument."""
    # Register namespace prefixes so ET.tostring uses readable names
    ET.register_namespace("office", NS["office"])
    ET.register_namespace("table", NS["table"])
    ET.register_namespace("text", NS["text"])

    root = ET.Element(f"{{{NS['office']}}}document-content")
    root.set(f"{{{NS['office']}}}version", "1.2")

    body = ET.SubElement(root, f"{{{NS['office']}}}body")
    spreadsheet = ET.SubElement(body, f"{{{NS['office']}}}spreadsheet")

    for sheet in doc.sheets:
        table = ET.SubElement(spreadsheet, f"{{{NS['table']}}}table")
        table.set(f"{{{NS['table']}}}name", sheet.name)
        for row in sheet.rows:
            row_el = ET.SubElement(table, f"{{{NS['table']}}}table-row")
            for cell in row.cells:
                row_el.append(_cell_to_xml(cell))

    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode").encode("utf-8")


def document_to_ods_bytes(doc: OdsDocument) -> bytes:
    """Serialize an OdsDocument to ODS ZIP bytes in memory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype MUST be first entry and stored uncompressed
        zf.writestr(
            zipfile.ZipInfo("mimetype", date_time=(2026, 1, 1, 0, 0, 0)),
            ODS_MIMETYPE,
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr("META-INF/manifest.xml", _MANIFEST_XML.strip())
        zf.writestr("content.xml", _build_content_xml(doc))
    return buf.getvalue()


def write_ods(doc: OdsDocument, path: str | Path) -> None:
    """Write an OdsDocument to an ODS file at the given path."""
    data = document_to_ods_bytes(doc)
    Path(path).write_bytes(data)


def set_cell_value(
    doc: OdsDocument,
    sheet_index: int,
    row: int,
    col: int,
    value: Any,
    value_type: str = "string",
) -> tuple[bool, str]:
    """Set a cell value in the OdsDocument (in-memory edit).

    Args:
        doc: OdsDocument to modify.
        sheet_index: 0-based sheet index.
        row: 0-based row index.
        col: 0-based column index.
        value: New cell value.
        value_type: ODF value type (string, float, date, boolean).

    Returns:
        (success, message) tuple.
    """
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False, f"Sheet index {sheet_index} out of range (0..{len(doc.sheets) - 1})"
    sheet = doc.sheets[sheet_index]
    # Extend rows if needed
    while row >= len(sheet.rows):
        sheet.rows.append(OdsRow(cells=[]))
    r = sheet.rows[row]
    # Extend cells if needed
    while col >= len(r.cells):
        r.cells.append(OdsCell())
    text = str(value) if value is not None else ""
    r.cells[col] = OdsCell(value=value, value_type=value_type, text=text)
    return True, f"Set ({sheet_index},{row},{col}) = {value!r}"


def add_sheet(doc: OdsDocument, name: str, position: int | None = None) -> tuple[bool, str]:
    """Add a new empty sheet to the OdsDocument.

    Args:
        doc: OdsDocument to modify.
        name: Name for the new sheet.
        position: Insert position (0-based). None = append at end.

    Returns:
        (success, message) tuple.
    """
    for s in doc.sheets:
        if s.name == name:
            return False, f"Sheet '{name}' already exists"
    sheet = OdsSheet(name=name, rows=[])
    if position is None or position >= len(doc.sheets):
        doc.sheets.append(sheet)
    else:
        doc.sheets.insert(max(0, position), sheet)
    return True, f"Added sheet '{name}'"


def remove_sheet(doc: OdsDocument, name: str) -> tuple[bool, str]:
    """Remove a sheet by name from the OdsDocument.

    Args:
        doc: OdsDocument to modify.
        name: Name of the sheet to remove.

    Returns:
        (success, message) tuple.
    """
    for i, s in enumerate(doc.sheets):
        if s.name == name:
            doc.sheets.pop(i)
            return True, f"Removed sheet '{name}'"
    return False, f"Sheet '{name}' not found"


def rename_sheet(doc: OdsDocument, old_name: str, new_name: str) -> tuple[bool, str]:
    """Rename a sheet in the OdsDocument.

    Args:
        doc: OdsDocument to modify.
        old_name: Current sheet name.
        new_name: New sheet name.

    Returns:
        (success, message) tuple.
    """
    for s in doc.sheets:
        if s.name == new_name:
            return False, f"Sheet '{new_name}' already exists"
    for s in doc.sheets:
        if s.name == old_name:
            s.name = new_name
            return True, f"Renamed '{old_name}' to '{new_name}'"
    return False, f"Sheet '{old_name}' not found"


def add_row(
    doc: OdsDocument,
    sheet_index: int,
    values: list[Any],
    value_type: str = "string",
) -> tuple[bool, str]:
    """Append a row of values to a sheet in the OdsDocument.

    Args:
        doc: OdsDocument to modify.
        sheet_index: 0-based sheet index.
        values: List of cell values for the new row.
        value_type: Default value type for cells.

    Returns:
        (success, message) tuple.
    """
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False, f"Sheet index {sheet_index} out of range"
    sheet = doc.sheets[sheet_index]
    cells = []
    for val in values:
        vt = value_type
        if isinstance(val, (int, float)) and value_type == "string":
            vt = "float"
        text = str(val) if val is not None else ""
        cells.append(OdsCell(value=val, value_type=vt, text=text))
    sheet.rows.append(OdsRow(cells=cells))
    return True, f"Added row with {len(values)} cells"


def delete_row(
    doc: OdsDocument,
    sheet_index: int,
    row: int,
) -> tuple[bool, str]:
    """Delete a row (0-based) from a sheet in the OdsDocument.

    Args:
        doc: OdsDocument to modify.
        sheet_index: 0-based sheet index.
        row: 0-based row index to delete.

    Returns:
        (success, message) tuple.
    """
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return False, f"Sheet index {sheet_index} out of range"
    sheet = doc.sheets[sheet_index]
    if row < 0 or row >= len(sheet.rows):
        return False, f"Row {row} out of range (0..{len(sheet.rows) - 1})"
    sheet.rows.pop(row)
    return True, f"Deleted row {row}"
