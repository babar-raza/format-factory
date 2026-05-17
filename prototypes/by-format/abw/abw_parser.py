"""
ABW prototype parser — Gate 4 acquisition prototype.

AbiWord (.abw) — plain XML AWML 1.0 format.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed, G3 passed.
Gate 4 prototype: this file.

Note: DTD at http://www.abisource.com/awml.dtd is unreachable (server down).
ElementTree disables DTD loading by default — XXE-safe.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ABW_ROOT_TAG = "abiword"
ABW_MIME = "application/x-abiword"


class AbwParseError(Exception):
    """Raised when ABW parsing fails."""


def parse_abw(source: str | bytes | Path) -> dict[str, Any]:
    """Parse an ABW flat XML document.

    Returns:
        Dict with is_abw, section_count, paragraph_count, paragraphs, error.
    """
    result: dict[str, Any] = {
        "is_abw": False,
        "section_count": 0,
        "paragraph_count": 0,
        "paragraphs": [],
        "error": None,
    }

    try:
        if isinstance(source, Path):
            xml_bytes = source.read_bytes()
        elif isinstance(source, str) and not source.strip().startswith("<") and not source.strip().startswith("<?"):
            xml_bytes = Path(source).read_bytes()
        elif isinstance(source, str):
            xml_bytes = source.encode("utf-8")
        elif isinstance(source, (bytes, bytearray)):
            xml_bytes = bytes(source)
        else:
            result["error"] = f"Unsupported source type: {type(source).__name__}"
            return result
    except OSError as exc:
        result["error"] = f"Cannot read file: {exc}"
        return result

    # Strip DOCTYPE declaration — ElementTree cannot resolve the DTD (server down)
    # and would otherwise raise an XMLSyntaxError on some platforms.
    # We strip only the DOCTYPE line; the rest of the XML is preserved.
    if isinstance(xml_bytes, bytes):
        xml_str = xml_bytes.decode("utf-8", errors="replace")
    else:
        xml_str = xml_bytes
    lines = xml_str.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("<!DOCTYPE")]
    clean_xml = "\n".join(filtered)

    try:
        root = ET.fromstring(clean_xml)
    except ET.ParseError as exc:
        result["error"] = f"XML parse error: {exc}"
        return result

    if root.tag != ABW_ROOT_TAG:
        result["error"] = f"Root element is not 'abiword' (got {root.tag!r})"
        return result

    result["is_abw"] = True

    sections = list(root.iter("section"))
    result["section_count"] = len(sections)

    paragraphs = []
    for p in root.iter("p"):
        text = "".join(p.itertext()).strip()
        paragraphs.append(text)

    result["paragraph_count"] = len(paragraphs)
    result["paragraphs"] = paragraphs
    return result


def count_sections(source: str | bytes | Path) -> int:
    return parse_abw(source)["section_count"]


def get_paragraph_count(source: str | bytes | Path) -> int:
    return parse_abw(source)["paragraph_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    parsed = parse_abw(source)
    return [p for p in parsed.get("paragraphs", []) if p]
