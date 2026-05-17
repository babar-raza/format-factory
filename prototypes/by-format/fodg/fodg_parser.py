"""
FODG prototype parser — Gate 4 acquisition prototype.

Flat OpenDocument Graphics (.fodg) — ODF 1.3 Part 3.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed_fast_path, G3 passed.
Gate 4 prototype: this file.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ODF namespace constants
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
}

FODG_MIME = "application/vnd.oasis.opendocument.graphics-flat-xml"


class FodgParseError(Exception):
    """Raised when FODG parsing fails."""


# Shape element tags to count
SHAPE_TAGS = {
    f"{{{NS['draw']}}}rect",
    f"{{{NS['draw']}}}ellipse",
    f"{{{NS['draw']}}}circle",
    f"{{{NS['draw']}}}line",
    f"{{{NS['draw']}}}polygon",
    f"{{{NS['draw']}}}polyline",
    f"{{{NS['draw']}}}path",
    f"{{{NS['draw']}}}frame",
    f"{{{NS['draw']}}}text-box",
    f"{{{NS['draw']}}}custom-shape",
    f"{{{NS['draw']}}}g",
}


def parse_fodg(source: str | bytes | Path) -> dict[str, Any]:
    """Parse a FODG flat drawing file.

    Returns:
        Dict with mime_type, is_fodg, page_count, pages, shapes_total, error.
    """
    result: dict[str, Any] = {
        "mime_type": None,
        "is_fodg": False,
        "page_count": 0,
        "pages": [],
        "shapes_total": 0,
        "error": None,
    }

    try:
        if isinstance(source, Path):
            xml_content = source.read_bytes()
        elif isinstance(source, str) and not source.strip().startswith("<"):
            xml_content = Path(source).read_bytes()
        elif isinstance(source, str):
            xml_content = source.encode("utf-8")
        else:
            xml_content = bytes(source)
    except OSError as exc:
        result["error"] = f"Cannot read file: {exc}"
        return result

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        result["error"] = f"XML parse error: {exc}"
        return result

    expected_tag = f"{{{NS['office']}}}document"
    if root.tag != expected_tag:
        result["error"] = f"Root element is not office:document (got {root.tag!r})"
        return result

    mime = root.get(f"{{{NS['office']}}}mimetype", "")
    result["mime_type"] = mime
    result["is_fodg"] = mime == FODG_MIME

    pages = []
    total_shapes = 0
    for page in root.iter(f"{{{NS['draw']}}}page"):
        page_info: dict[str, Any] = {
            "name": page.get(f"{{{NS['draw']}}}name", ""),
            "style": page.get(f"{{{NS['draw']}}}style-name", ""),
            "master_page": page.get(f"{{{NS['draw']}}}master-page-name", ""),
            "shape_count": 0,
            "text_content": [],
        }
        # Count direct shapes in this page (not recursive — avoid double counting groups)
        for child in page:
            if child.tag in SHAPE_TAGS:
                page_info["shape_count"] += 1
                total_shapes += 1
        # Extract text from any text elements on the page
        for tp in page.iter(f"{{{NS['text']}}}p"):
            t = "".join(tp.itertext()).strip()
            if t:
                page_info["text_content"].append(t)
        pages.append(page_info)

    result["page_count"] = len(pages)
    result["pages"] = pages
    result["shapes_total"] = total_shapes
    return result


def count_pages(source: str | bytes | Path) -> int:
    return parse_fodg(source)["page_count"]


def get_shape_count(source: str | bytes | Path) -> int:
    return parse_fodg(source)["shapes_total"]


def extract_text(source: str | bytes | Path) -> list[str]:
    parsed = parse_fodg(source)
    texts = []
    for page in parsed.get("pages", []):
        texts.extend(page.get("text_content", []))
    return [t for t in texts if t]
