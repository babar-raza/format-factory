"""
Gnumeric codec — minimal Gnumeric spreadsheet API.

Gnumeric (.gnumeric) — gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Uses gzip + xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
"""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Gnumeric XML namespace
GNM_NS = "http://www.gnumeric.org/v10.dtd"
GNM_MIME = "application/x-gnumeric"

# Gzip magic bytes
GZIP_MAGIC = b"\x1f\x8b"

# Maximum compressed file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024


class GnumericError(Exception):
    """Base exception for Gnumeric codec errors."""


class GnumericParseError(GnumericError):
    """Raised when Gnumeric parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse a Gnumeric file.

    The returned model contains:
        is_gnumeric (bool): True if valid Gnumeric file.
        sheet_count (int): Number of gnm:Sheet elements.
        sheets (list[dict]): Per-sheet data.
        cell_count (int): Total cell count across all sheets.

    Args:
        source: Path to .gnumeric file or bytes.

    Returns:
        Parsed workbook model dict.

    Raises:
        GnumericParseError: If source cannot be parsed.
        GnumericError: For other load errors.
    """
    raw = _read_source(source)
    xml_bytes = _decompress(raw)
    root = _parse_xml(xml_bytes)
    return _build_model(root)


def get_sheet_count(source: str | bytes | Path) -> int:
    """Return number of sheets in the workbook."""
    return load(source)["sheet_count"]


def get_cell_count(source: str | bytes | Path) -> int:
    """Return total cell count across all sheets."""
    return load(source)["cell_count"]


def extract_values(source: str | bytes | Path) -> list[str]:
    """Extract all non-empty cell values from all sheets."""
    model = load(source)
    values: list[str] = []
    for sheet in model.get("sheets", []):
        values.extend(sheet.get("cell_values", []))
    return [v for v in values if v]


def get_sheet_metadata(source: str | bytes | Path) -> list[dict[str, Any]]:
    """Return per-sheet metadata list.

    Each dict contains: name, cell_count, cell_values.
    """
    return load(source).get("sheets", [])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_source(source: str | bytes | Path) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str) and not source.strip().startswith("<"):
        path = Path(source)
        _check_size(path)
        return path.read_bytes()
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise GnumericError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise GnumericError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise GnumericParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise GnumericError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _decompress(raw: bytes) -> bytes:
    if raw[:2] == GZIP_MAGIC:
        try:
            return gzip.decompress(raw)
        except OSError as exc:
            raise GnumericParseError(f"Gzip decompression failed: {exc}") from exc
    return raw


def _parse_xml(xml_bytes: bytes) -> ET.Element:
    """Parse XML bytes safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise GnumericParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a workbook model from the parsed XML root."""
    expected_tag = f"{{{GNM_NS}}}Workbook"
    if root.tag != expected_tag:
        raise GnumericParseError(
            f"Root element must be gnm:Workbook, got {root.tag!r}"
        )

    sheets = _extract_sheets(root)
    total_cells = sum(s["cell_count"] for s in sheets)

    return {
        "is_gnumeric": True,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "cell_count": total_cells,
    }


def _extract_sheets(root: ET.Element) -> list[dict[str, Any]]:
    """Extract per-sheet metadata from all gnm:Sheet elements."""
    sheets = []
    for sheet in root.iter(f"{{{GNM_NS}}}Sheet"):
        name_el = sheet.find(f"{{{GNM_NS}}}Name")
        name = name_el.text if name_el is not None and name_el.text else ""
        cells = list(sheet.iter(f"{{{GNM_NS}}}Cell"))
        cell_values = []
        for cell in cells:
            val_el = cell.find(f"{{{GNM_NS}}}Value")
            if val_el is not None and val_el.text:
                cell_values.append(val_el.text.strip())
        sheets.append({
            "name": name,
            "cell_count": len(cells),
            "cell_values": cell_values,
        })
    return sheets
