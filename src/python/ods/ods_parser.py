"""
ods_parser.py — ODS streaming parser for format-factory-ods.

Public API:
  parse_ods(file_path)        — returns OdsDocument or error dict
  parse_ods_strict(file_path) — raises OdsError on failure
  probe_ods(file_path)        — returns header/metadata dict without full parse

Implements Gate 4 prototype scope per R26 parser plan.
Technology: Python zipfile + xml.etree.ElementTree (stdlib, XXE-safe).

License: Apache-2.0
"""

from __future__ import annotations

import os
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ODS constants
ODS_MIMETYPE = "application/vnd.oasis.opendocument.spreadsheet"
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ZIP_ENTRIES = 1000
MAX_COLUMNS = 1024
MAX_ROWS = 1048576

# ODF namespaces
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}


UNSUPPORTED_FEATURES = frozenset({
    "formulas",
    "formula_evaluation",
    "charts",
    "pivot_tables",
    "conditional_formatting",
    "data_validation",
    "macros",
    "embedded_objects",
    "images",
    "named_ranges",
    "cell_styles",
    "merged_cells",
    "filters",
    "comments",
    "protection",
    "encryption",
    "external_links",
})

SUPPORTED_FEATURES = frozenset({
    "sheet_enumeration",
    "cell_text_extraction",
    "cell_value_type_detection",
    "float_value_parsing",
    "date_value_extraction",
    "boolean_value_extraction",
    "row_repeat_expansion",
    "column_repeat_expansion",
    "container_validation",
    "mimetype_verification",
    "size_guard",
    "probe_without_parse",
})


def get_capabilities() -> dict[str, Any]:
    """Return supported/unsupported feature declarations for ODS parser."""
    return {
        "format": "ods",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
        "max_file_size": MAX_FILE_SIZE,
        "max_zip_entries": MAX_ZIP_ENTRIES,
        "max_columns": MAX_COLUMNS,
        "max_rows": MAX_ROWS,
    }


class OdsError(Exception):
    """Base exception for ODS parser errors."""


class OdsInvalidContainerError(OdsError):
    """Raised when the ZIP container is invalid or missing required entries."""


class OdsSizeError(OdsError):
    """Raised when the file or decompressed content exceeds size limits."""


@dataclass
class OdsCell:
    value: str | float | None = None
    value_type: str = ""
    text: str = ""


@dataclass
class OdsRow:
    cells: list[OdsCell] = field(default_factory=list)


@dataclass
class OdsSheet:
    name: str = ""
    rows: list[OdsRow] = field(default_factory=list)


@dataclass
class OdsDocument:
    sheets: list[OdsSheet] = field(default_factory=list)
    path: str = ""


def _check_file_size(path: Path) -> None:
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise OdsSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
        )


def _validate_container(zf: zipfile.ZipFile) -> None:
    names = zf.namelist()
    if len(names) > MAX_ZIP_ENTRIES:
        raise OdsSizeError(
            f"ZIP has {len(names)} entries, exceeds limit of {MAX_ZIP_ENTRIES}"
        )
    if "mimetype" not in names:
        raise OdsInvalidContainerError("Missing 'mimetype' entry in ODS container")
    mimetype = zf.read("mimetype").decode("utf-8", errors="replace").strip()
    if mimetype != ODS_MIMETYPE:
        raise OdsInvalidContainerError(
            f"Invalid mimetype: expected '{ODS_MIMETYPE}', got '{mimetype}'"
        )
    if "content.xml" not in names:
        raise OdsInvalidContainerError("Missing 'content.xml' in ODS container")
    # Check total decompressed size
    total = sum(info.file_size for info in zf.infolist())
    if total > MAX_FILE_SIZE:
        raise OdsSizeError(
            f"Total decompressed size {total} exceeds limit of {MAX_FILE_SIZE}"
        )


def _extract_text(elem: ET.Element) -> str:
    """Extract text from text:p elements within a cell."""
    parts = []
    for p in elem.findall(f"{{{NS['text']}}}p"):
        text = "".join(p.itertext())
        parts.append(text)
    return "\n".join(parts)


def _parse_cell(elem: ET.Element) -> OdsCell:
    vtype = elem.get(f"{{{NS['office']}}}value-type", "")
    text = _extract_text(elem)
    value: str | float | None = None

    if vtype == "float" or vtype == "percentage" or vtype == "currency":
        raw = elem.get(f"{{{NS['office']}}}value", "")
        try:
            value = float(raw)
        except (ValueError, TypeError):
            value = text
    elif vtype == "date":
        value = elem.get(f"{{{NS['office']}}}date-value", text)
    elif vtype == "boolean":
        value = elem.get(f"{{{NS['office']}}}boolean-value", text)
    elif vtype == "string" or vtype == "":
        value = text
    else:
        value = text

    return OdsCell(value=value, value_type=vtype, text=text)


def _parse_content_xml(content_bytes: bytes) -> list[OdsSheet]:
    root = ET.fromstring(content_bytes)
    sheets: list[OdsSheet] = []

    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return sheets
    spreadsheet = body.find(f"{{{NS['office']}}}spreadsheet")
    if spreadsheet is None:
        return sheets

    for table in spreadsheet.findall(f"{{{NS['table']}}}table"):
        sheet_name = table.get(f"{{{NS['table']}}}name", "")
        sheet = OdsSheet(name=sheet_name)

        for row_elem in table.findall(f"{{{NS['table']}}}table-row"):
            row_repeat_str = row_elem.get(
                f"{{{NS['table']}}}number-rows-repeated", "1"
            )
            try:
                row_repeat = min(int(row_repeat_str), MAX_ROWS)
            except ValueError:
                row_repeat = 1

            row = OdsRow()
            for cell_elem in row_elem.findall(f"{{{NS['table']}}}table-cell"):
                col_repeat_str = cell_elem.get(
                    f"{{{NS['table']}}}number-columns-repeated", "1"
                )
                try:
                    col_repeat = min(int(col_repeat_str), MAX_COLUMNS)
                except ValueError:
                    col_repeat = 1

                cell = _parse_cell(cell_elem)
                for _ in range(col_repeat):
                    row.cells.append(
                        OdsCell(
                            value=cell.value,
                            value_type=cell.value_type,
                            text=cell.text,
                        )
                    )

            # Only add non-empty rows (skip trailing empty repeated rows)
            if any(c.text or c.value_type for c in row.cells):
                for _ in range(row_repeat):
                    sheet.rows.append(row)

        sheets.append(sheet)

    return sheets


def parse_ods_strict(file_path: str | Path) -> OdsDocument:
    """Parse an ODS file, raising OdsError on any problem."""
    path = Path(file_path)
    _check_file_size(path)
    try:
        with zipfile.ZipFile(path, "r") as zf:
            _validate_container(zf)
            content = zf.read("content.xml")
    except zipfile.BadZipFile as exc:
        raise OdsInvalidContainerError(f"Invalid ZIP: {exc}") from exc
    except OdsError:
        raise
    except OSError as exc:
        raise OdsError(f"Cannot read file: {exc}") from exc

    sheets = _parse_content_xml(content)
    return OdsDocument(sheets=sheets, path=str(path))


def parse_ods(file_path: str | Path) -> dict[str, Any]:
    """Parse an ODS file, returning a result dict (never raises)."""
    try:
        doc = parse_ods_strict(file_path)
        return {
            "ok": True,
            "path": doc.path,
            "sheet_count": len(doc.sheets),
            "sheets": [
                {
                    "name": s.name,
                    "row_count": len(s.rows),
                    "rows": [
                        {"cells": [{"value": c.value, "value_type": c.value_type, "text": c.text} for c in r.cells]}
                        for r in s.rows
                    ],
                }
                for s in doc.sheets
            ],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_ods(file_path: str | Path) -> dict[str, Any]:
    """Probe an ODS file for basic metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        _check_file_size(path)
        with zipfile.ZipFile(path, "r") as zf:
            _validate_container(zf)
            result["valid_container"] = True
            result["entries"] = zf.namelist()
            result["mimetype"] = zf.read("mimetype").decode("utf-8", errors="replace").strip()
    except Exception as exc:
        result["valid_container"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Rnext15 — ODS accessor functions
# ---------------------------------------------------------------------------


def get_cell_value(
    file_path: str | Path, sheet_index: int, row: int, col: int
) -> Any:
    """Return the value at (sheet_index, row, col) in an ODS file (all 0-based).

    Returns None if the coordinates are out of range.

    Args:
        file_path:    Path to ODS file.
        sheet_index:  0-based sheet index.
        row:          0-based row index.
        col:          0-based column index.

    Returns:
        Cell value (str, float, or None).

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return None
    sheet = doc.sheets[sheet_index]
    if row < 0 or row >= len(sheet.rows):
        return None
    r = sheet.rows[row]
    if col < 0 or col >= len(r.cells):
        return None
    return r.cells[col].value


def get_sheet_names(file_path: str | Path) -> list[str]:
    """Return the list of sheet names in an ODS file.

    Args:
        file_path: Path to ODS file.

    Returns:
        List of sheet name strings.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    return [s.name for s in doc.sheets]


def get_row_count(file_path: str | Path, sheet_index: int = 0) -> int:
    """Return the number of non-empty rows in a given sheet (0-based index).

    Args:
        file_path:    Path to ODS file.
        sheet_index:  0-based sheet index (default 0).

    Returns:
        Integer row count. Returns 0 if sheet_index is out of range.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    return len(doc.sheets[sheet_index].rows)


def get_column_count(file_path: str | Path, sheet_index: int = 0) -> int:
    """Return the maximum number of columns in any row of a given sheet.

    Args:
        file_path:    Path to ODS file.
        sheet_index:  0-based sheet index (default 0).

    Returns:
        Integer column count. Returns 0 if sheet has no rows or sheet_index is out of range.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    if not sheet.rows:
        return 0
    return max(len(r.cells) for r in sheet.rows)


def get_row_values(
    file_path: str | Path, sheet_index: int, row: int
) -> list[Any]:
    """Return all cell values for a given row (0-based) as a list.

    Args:
        file_path:    Path to ODS file.
        sheet_index:  0-based sheet index.
        row:          0-based row index.

    Returns:
        List of cell values. Returns empty list if row or sheet is out of range.

    Raises:
        OdsError subclasses on parse failure.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return []
    sheet = doc.sheets[sheet_index]
    if row < 0 or row >= len(sheet.rows):
        return []
    return [c.value for c in sheet.rows[row].cells]


def count_sheets(file_path: str | Path) -> int:
    """Return the number of sheets in an ODS file."""
    doc = parse_ods_strict(file_path)
    return len(doc.sheets)


def get_all_values(file_path: str | Path, sheet_index: int = 0) -> list[Any]:
    """Return a flat list of all cell values in a sheet, row by row."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return []
    sheet = doc.sheets[sheet_index]
    result: list[Any] = []
    for row in sheet.rows:
        for cell in row.cells:
            result.append(cell.value)
    return result


def get_cell_count(file_path: str | Path, sheet_index: int = 0) -> int:
    """Return the total number of cells in a sheet."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    return sum(len(row.cells) for row in sheet.rows)


def ods_to_csv(file_path: str | Path, sheet_index: int = 0) -> str:
    """Export an ODS sheet as a CSV string.

    Args:
        file_path: Path to ODS file.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        CSV string. Empty string if sheet not found.
    """
    import csv as csv_mod
    import io
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return ""
    sheet = doc.sheets[sheet_index]
    buf = io.StringIO()
    writer = csv_mod.writer(buf, lineterminator="\r\n")
    for row in sheet.rows:
        csv_row = []
        for cell in row.cells:
            val = cell.value
            if val is None:
                csv_row.append("")
            elif isinstance(val, float) and val == int(val):
                csv_row.append(str(int(val)))
            else:
                csv_row.append(str(val))
        writer.writerow(csv_row)
    return buf.getvalue()


def get_column_values(file_path: str | Path, col: int, sheet_index: int = 0) -> list[Any]:
    """Return all values in a column (0-based) from a given sheet.

    Args:
        file_path: Path to ODS file.
        col: 0-based column index.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        List of cell values. None for missing cells.
    """
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return []
    sheet = doc.sheets[sheet_index]
    result: list[Any] = []
    for row in sheet.rows:
        if col < len(row.cells):
            result.append(row.cells[col].value)
        else:
            result.append(None)
    return result
