"""
ABW codec — minimal AbiWord document API.

AbiWord (.abw) — plain XML AWML 1.0 format.
Uses xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false

Security note: DOCTYPE declarations are stripped before parsing.
The DTD at http://www.abisource.com/awml.dtd is unreachable (server down),
and ElementTree does not resolve external DTDs anyway (XXE-safe).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ABW_ROOT_TAG = "abiword"
ABW_MIME = "application/x-abiword"

# Maximum file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024


class AbwError(Exception):
    """Base exception for ABW codec errors."""


class AbwParseError(AbwError):
    """Raised when ABW parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse an ABW document.

    The returned model contains:
        is_abw (bool): True if valid AbiWord document.
        section_count (int): Number of <section> elements.
        paragraph_count (int): Number of <p> elements.
        paragraphs (list[str]): Text content of each paragraph.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Parsed document model dict.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    xml_bytes = _read_source(source)
    clean = _strip_doctype(xml_bytes)
    root = _parse_xml(clean)
    return _build_model(root)


def get_section_count(source: str | bytes | Path) -> int:
    """Return number of sections."""
    return load(source)["section_count"]


def get_paragraph_count(source: str | bytes | Path) -> int:
    """Return total paragraph count."""
    return load(source)["paragraph_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all non-empty paragraph texts."""
    model = load(source)
    return [p for p in model.get("paragraphs", []) if p]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_source(source: str | bytes | Path) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str) and not source.strip().startswith("<") and not source.strip().startswith("<?"):
        path = Path(source)
        _check_size(path)
        return path.read_bytes()
    elif isinstance(source, str):
        return source.encode("utf-8")
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise AbwError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise AbwError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise AbwParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise AbwError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _strip_doctype(xml_bytes: bytes) -> str:
    """Strip DOCTYPE declaration to avoid DTD resolution attempts."""
    xml_str = xml_bytes.decode("utf-8", errors="replace")
    lines = xml_str.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("<!DOCTYPE")]
    return "\n".join(filtered)


def _parse_xml(xml_str: str) -> ET.Element:
    """Parse XML string safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_str)
    except ET.ParseError as exc:
        raise AbwParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a document model from the parsed XML root."""
    if root.tag != ABW_ROOT_TAG:
        raise AbwParseError(
            f"Root element must be 'abiword', got {root.tag!r}"
        )

    sections = list(root.iter("section"))
    paragraphs = []
    for p in root.iter("p"):
        text = "".join(p.itertext()).strip()
        paragraphs.append(text)

    return {
        "is_abw": True,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }
