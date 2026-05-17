"""
FODP prototype parser — Gate 4 acquisition prototype.

Flat OpenDocument Presentation (.fodp) — ODF 1.3 Part 3.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed_fast_path, G3 passed.
Gate 4 prototype: this file.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ODF namespace constants (ODF 1.3 Part 3)
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "dc": "http://purl.org/dc/elements/1.1/",
}

FODP_MIME = "application/vnd.oasis.opendocument.presentation-flat-xml"
FODG_MIME = "application/vnd.oasis.opendocument.graphics-flat-xml"


class FodpParseError(Exception):
    """Raised when FODP parsing fails."""


def parse_fodp(source: str | bytes | Path) -> dict[str, Any]:
    """Parse a FODP flat presentation file.

    Args:
        source: Path to .fodp file, bytes content, or string XML content.

    Returns:
        Dict with:
            mime_type (str): office:mimetype attribute value.
            is_fodp (bool): True if mime_type matches FODP.
            page_count (int): Number of draw:page elements.
            pages (list[dict]): Per-page metadata.
            styles_count (int): Number of style:style elements.
            error (str | None): Error message if parsing failed.
    """
    result: dict[str, Any] = {
        "mime_type": None,
        "is_fodp": False,
        "page_count": 0,
        "pages": [],
        "styles_count": 0,
        "error": None,
    }

    # Load source
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

    # Parse XML (XXE-safe: no external entities in ElementTree)
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        result["error"] = f"XML parse error: {exc}"
        return result

    # Check root element and mimetype
    expected_tag = f"{{{NS['office']}}}document"
    if root.tag != expected_tag:
        result["error"] = (
            f"Root element is not office:document (got {root.tag!r})"
        )
        return result

    mime = root.get(f"{{{NS['office']}}}mimetype", "")
    result["mime_type"] = mime
    result["is_fodp"] = mime == FODP_MIME

    # Count pages (draw:page elements in office:body/office:presentation)
    pages = []
    for page in root.iter(f"{{{NS['draw']}}}page"):
        page_info: dict[str, Any] = {
            "name": page.get(f"{{{NS['draw']}}}name", ""),
            "style": page.get(f"{{{NS['draw']}}}style-name", ""),
            "master_page": page.get(
                f"{{{NS['draw']}}}master-page-name", ""
            ),
            "title": None,
            "text_content": [],
            "shape_count": 0,
        }

        # Extract title from presentation:title shapes
        for frame in page.iter(f"{{{NS['draw']}}}frame"):
            pres_class = frame.get(
                f"{{{NS['presentation']}}}class", ""
            )
            texts = []
            for tp in frame.iter(f"{{{NS['text']}}}p"):
                t = "".join(tp.itertext()).strip()
                if t:
                    texts.append(t)
            if pres_class == "title" and texts:
                page_info["title"] = texts[0]
            page_info["text_content"].extend(texts)
            page_info["shape_count"] += 1

        pages.append(page_info)

    result["page_count"] = len(pages)
    result["pages"] = pages

    # Count styles
    styles = root.findall(
        f".//{{{NS['style']}}}style"
    )
    result["styles_count"] = len(styles)

    return result


def count_pages(source: str | bytes | Path) -> int:
    """Return the number of slides/pages in a FODP file."""
    return parse_fodp(source)["page_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all text strings from all slides."""
    parsed = parse_fodp(source)
    texts = []
    for page in parsed.get("pages", []):
        texts.extend(page.get("text_content", []))
    return [t for t in texts if t]


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) < 2:
        print("Usage: fodp_parser.py <file.fodp>")
        sys.exit(1)
    result = parse_fodp(sys.argv[1])
    print(json.dumps(result, indent=2))
