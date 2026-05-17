"""
Gnumeric prototype parser — Gate 4 acquisition prototype.

Gnumeric (.gnumeric) — gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed, G3 passed.
Gate 4 prototype: this file.
"""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Gnumeric XML namespace
GNM_NS = "http://www.gnumeric.org/v10.dtd"
GNM_MIME = "application/x-gnumeric"

# Magic bytes: gzip magic
GZIP_MAGIC = b"\x1f\x8b"


class GnumericParseError(Exception):
    """Raised when Gnumeric parsing fails."""


def parse_gnumeric(source: str | bytes | Path) -> dict[str, Any]:
    """Parse a Gnumeric file.

    Returns:
        Dict with is_gnumeric, sheet_count, sheets, cell_count, error.
    """
    result: dict[str, Any] = {
        "is_gnumeric": False,
        "sheet_count": 0,
        "sheets": [],
        "cell_count": 0,
        "error": None,
    }

    try:
        if isinstance(source, Path):
            raw = source.read_bytes()
        elif isinstance(source, str) and not source.strip().startswith("<"):
            raw = Path(source).read_bytes()
        elif isinstance(source, (bytes, bytearray)):
            raw = bytes(source)
        else:
            result["error"] = f"Unsupported source type: {type(source).__name__}"
            return result
    except OSError as exc:
        result["error"] = f"Cannot read file: {exc}"
        return result

    # Decompress if gzip
    if raw[:2] == GZIP_MAGIC:
        try:
            xml_bytes = gzip.decompress(raw)
        except OSError as exc:
            result["error"] = f"Gzip decompression failed: {exc}"
            return result
    else:
        xml_bytes = raw

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        result["error"] = f"XML parse error: {exc}"
        return result

    expected_tag = f"{{{GNM_NS}}}Workbook"
    if root.tag != expected_tag:
        result["error"] = f"Root element is not gnm:Workbook (got {root.tag!r})"
        return result

    result["is_gnumeric"] = True

    sheets = []
    total_cells = 0
    for sheet in root.iter(f"{{{GNM_NS}}}Sheet"):
        name_el = sheet.find(f"{{{GNM_NS}}}Name")
        name = name_el.text if name_el is not None and name_el.text else ""
        cells = list(sheet.iter(f"{{{GNM_NS}}}Cell"))
        cell_count = len(cells)
        total_cells += cell_count
        # Extract cell text values
        cell_values = []
        for cell in cells:
            val_el = cell.find(f"{{{GNM_NS}}}Value")
            if val_el is not None and val_el.text:
                cell_values.append(val_el.text.strip())
        sheets.append({
            "name": name,
            "cell_count": cell_count,
            "cell_values": cell_values,
        })

    result["sheet_count"] = len(sheets)
    result["sheets"] = sheets
    result["cell_count"] = total_cells
    return result


def count_sheets(source: str | bytes | Path) -> int:
    return parse_gnumeric(source)["sheet_count"]


def get_cell_count(source: str | bytes | Path) -> int:
    return parse_gnumeric(source)["cell_count"]


def extract_values(source: str | bytes | Path) -> list[str]:
    parsed = parse_gnumeric(source)
    values: list[str] = []
    for sheet in parsed.get("sheets", []):
        values.extend(sheet.get("cell_values", []))
    return [v for v in values if v]
