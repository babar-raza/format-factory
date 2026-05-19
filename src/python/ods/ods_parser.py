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
