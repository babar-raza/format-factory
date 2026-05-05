"""
fods_parser.py — FODS (Flat OpenDocument Spreadsheet) prototype parser.

Gate 4 prototype — format-factory project.
Evidence artifact: prototypes/by-format/fods/fods_parser.py

Uses Python stdlib only (xml.etree.ElementTree).
No formula evaluation. No style resolution. No external dependencies.
No network access. No file writes unless output_path is specified via CLI.

Security notes:
- xml.etree.ElementTree does NOT expand external entities in Python 3.8+.
  ExpatParser used by ET does not process DTD external entity references.
  Safe for trusted FODS files (prototype scope: Gate 3 synthetic samples).
- File size guard: rejects files > MAX_FILE_BYTES (100 MB).
- No subprocess calls. No file writes on parse-only path.
- XXE: stdlib ET is safe for files without DTD entity declarations.
- Full production hardening is Gate 8 scope (defusedxml, size limits, recursion guards).

ODF 1.3 spec citation:
  source: ODF 1.3 Part 3 (schema spec)
  source_hash: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-05 (run029)
"""

from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_MIMETYPE: str = (
    "application/vnd.oasis.opendocument.spreadsheet-flat-xml"
)
MAX_FILE_BYTES: int = 100 * 1024 * 1024  # 100 MB guard

# ODF 1.3 XML namespace URIs (ODF 1.3 §3.1.2 — PR-010)
_NS_OFFICE: str = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TABLE: str  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
_NS_TEXT: str   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"

# Qualified element names (Clark notation: {uri}localname)
_QN_DOCUMENT    = f"{{{_NS_OFFICE}}}document"
_QN_BODY        = f"{{{_NS_OFFICE}}}body"
_QN_SPREADSHEET = f"{{{_NS_OFFICE}}}spreadsheet"
_QN_TABLE       = f"{{{_NS_TABLE}}}table"
_QN_ROW         = f"{{{_NS_TABLE}}}table-row"
_QN_CELL        = f"{{{_NS_TABLE}}}table-cell"
_QN_COVERED     = f"{{{_NS_TABLE}}}covered-table-cell"
_QN_TEXT_P      = f"{{{_NS_TEXT}}}p"

# Qualified attribute names
_ATTR_MIMETYPE   = f"{{{_NS_OFFICE}}}mimetype"
_ATTR_VERSION    = f"{{{_NS_OFFICE}}}version"
_ATTR_VALUE_TYPE = f"{{{_NS_OFFICE}}}value-type"
_ATTR_VALUE      = f"{{{_NS_OFFICE}}}value"
_ATTR_BOOL_VALUE = f"{{{_NS_OFFICE}}}boolean-value"
_ATTR_DATE_VALUE = f"{{{_NS_OFFICE}}}date-value"
_ATTR_TIME_VALUE = f"{{{_NS_OFFICE}}}time-value"
_ATTR_TABLE_NAME = f"{{{_NS_TABLE}}}name"
_ATTR_COL_REPEAT = f"{{{_NS_TABLE}}}number-columns-repeated"
_ATTR_ROW_REPEAT = f"{{{_NS_TABLE}}}number-rows-repeated"
_ATTR_FORMULA    = f"{{{_NS_TABLE}}}formula"

# Max repeated empty cells/rows to expand (prevents large allocations for
# trailing-empty-cell patterns common in FODS from spreadsheet editors).
_MAX_EXPAND_REPEAT: int = 128


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_fods(file_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Parse a FODS file and return a normalized dict.

    Args:
        file_path: Path to the .fods file.

    Returns:
        Dict with keys:
          format (str), spec_version (str), odf_version_attr (str),
          mimetype (str|None), sheet_count (int), sheets (list), warnings (list).
        On fatal parse error, returns dict with 'error' key.

    This function does not raise. All errors are returned in the result dict.
    """
    path = Path(file_path)
    warnings: list[str] = []

    # --- File guards ---
    if not path.exists():
        return {"error": f"File not found: {path}"}
    if not path.is_file():
        return {"error": f"Not a regular file: {path}"}
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        return {"error": f"File too large: {size} bytes (max {MAX_FILE_BYTES})"}

    # --- XML parse (PR-001) ---
    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        return {"error": f"XML parse error: {exc}"}

    root = tree.getroot()

    # --- Root element check (PR-001) ---
    if root.tag != _QN_DOCUMENT:
        return {
            "error": (
                f"Root element is not office:document "
                f"(got {root.tag!r}); not a valid FODS file"
            )
        }

    # --- Mimetype validation (PR-002) ---
    mimetype = root.get(_ATTR_MIMETYPE, "")
    if not mimetype:
        warnings.append("office:mimetype attribute is absent on root element")
    elif mimetype != EXPECTED_MIMETYPE:
        warnings.append(
            f"Unexpected mimetype: {mimetype!r} "
            f"(expected {EXPECTED_MIMETYPE!r})"
        )

    version = root.get(_ATTR_VERSION, "")

    # --- Navigate to office:body / office:spreadsheet (PR-003) ---
    body = root.find(_QN_BODY)
    if body is None:
        return {"error": "office:body element not found"}
    spreadsheet = body.find(_QN_SPREADSHEET)
    if spreadsheet is None:
        return {
            "error": (
                "office:spreadsheet element not found inside office:body; "
                "document may not be a spreadsheet FODS"
            )
        }

    # --- Enumerate sheets (PR-004) ---
    sheets: list[dict[str, Any]] = []
    for table_elem in spreadsheet:
        if table_elem.tag != _QN_TABLE:
            continue  # skip table:named-expressions, table:database-ranges, etc.
        sheet_name = table_elem.get(_ATTR_TABLE_NAME, "")
        rows = _parse_rows(table_elem, warnings)
        sheets.append(
            {
                "name": sheet_name,
                "row_count": len(rows),
                "rows": rows,
            }
        )

    return {
        "format": "fods",
        "spec_version": "ODF 1.3",
        "odf_version_attr": version,
        "mimetype": mimetype if mimetype else None,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_rows(
    table_elem: ET.Element, warnings: list[str]
) -> list[dict[str, Any]]:
    """Parse all rows in a table:table element (PR-005)."""
    rows: list[dict[str, Any]] = []
    row_index = 0

    for row_elem in table_elem:
        if row_elem.tag != _QN_ROW:
            continue  # skip table:table-column, table:table-header-rows, etc.

        row_repeat = int(row_elem.get(_ATTR_ROW_REPEAT, 1))
        if row_repeat > _MAX_EXPAND_REPEAT:
            warnings.append(
                f"Row at logical index {row_index} has "
                f"table:number-rows-repeated={row_repeat}; "
                f"capping expansion at {_MAX_EXPAND_REPEAT}"
            )
            row_repeat = _MAX_EXPAND_REPEAT

        cells = _parse_cells(row_elem, warnings, row_index)

        for _ in range(row_repeat):
            rows.append(
                {
                    "index": row_index,
                    "cells": cells,
                }
            )
            row_index += 1

    return rows


def _parse_cells(
    row_elem: ET.Element,
    warnings: list[str],
    row_index: int,
) -> list[dict[str, Any]]:
    """Parse all cells in a table:table-row element (PR-006, PR-007)."""
    cells: list[dict[str, Any]] = []
    col_index = 0

    for cell_elem in row_elem:
        if cell_elem.tag not in (_QN_CELL, _QN_COVERED):
            continue

        col_repeat = int(cell_elem.get(_ATTR_COL_REPEAT, 1))
        value_type: str | None = cell_elem.get(_ATTR_VALUE_TYPE)
        value = _extract_value(cell_elem, value_type, warnings)
        text = _extract_text(cell_elem)
        formula: str | None = cell_elem.get(_ATTR_FORMULA)  # PR-009

        is_empty = (
            value_type is None
            and value is None
            and text is None
            and formula is None
        )

        # Cap column repeat for empty trailing cells only (PR-007)
        effective_repeat = col_repeat
        if is_empty and col_repeat > _MAX_EXPAND_REPEAT:
            warnings.append(
                f"Row {row_index} col {col_index}: empty cell has "
                f"table:number-columns-repeated={col_repeat}; "
                f"recording first occurrence only to avoid large allocation"
            )
            effective_repeat = 1

        for _ in range(effective_repeat):
            cell_entry: dict[str, Any] = {
                "col_index": col_index,
                "value_type": value_type,
                "value": value,
                "text": text,
                "formula": formula,
            }
            if cell_elem.tag == _QN_COVERED:
                cell_entry["covered"] = True
            cells.append(cell_entry)
            col_index += 1

    return cells


def _extract_value(
    cell_elem: ET.Element,
    value_type: str | None,
    warnings: list[str],
) -> Any:
    """Extract the typed attribute value from a cell element (PR-006)."""
    if value_type is None:
        return None
    if value_type == "string":
        # String cell value is in text:p children (PR-008), not an attribute
        return None
    if value_type == "float":
        raw = cell_elem.get(_ATTR_VALUE)
        if raw is None:
            warnings.append("float cell missing office:value attribute")
            return None
        try:
            return float(raw)
        except ValueError:
            warnings.append(f"Invalid float value: {raw!r}")
            return None
    if value_type == "boolean":
        raw = cell_elem.get(_ATTR_BOOL_VALUE)
        if raw is None:
            warnings.append("boolean cell missing office:boolean-value attribute")
            return None
        return raw.lower() == "true"
    if value_type == "date":
        return cell_elem.get(_ATTR_DATE_VALUE)
    if value_type == "time":
        return cell_elem.get(_ATTR_TIME_VALUE)
    if value_type in ("currency", "percentage"):
        raw = cell_elem.get(_ATTR_VALUE)
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            warnings.append(f"Invalid {value_type} value: {raw!r}")
            return None
    warnings.append(f"Unsupported value-type: {value_type!r}; value set to null")
    return None


def _extract_text(cell_elem: ET.Element) -> str | None:
    """Concatenate text from all text:p children (PR-008).

    Multiple text:p elements are joined with newline.
    Returns None if no text:p children or all are empty.
    """
    parts: list[str] = []
    for child in cell_elem:
        if child.tag == _QN_TEXT_P:
            text = "".join(child.itertext())
            if text:
                parts.append(text)
    return "\n".join(parts) if parts else None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Command-line interface: parse one FODS file, print JSON to stdout."""
    if len(sys.argv) < 2:
        print(
            "Usage: python fods_parser.py <file.fods> [output.json]",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_path: str | None = sys.argv[2] if len(sys.argv) > 2 else None

    result = parse_fods(input_path)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Output written to: {output_path}", file=sys.stderr)
    else:
        print(output)

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
