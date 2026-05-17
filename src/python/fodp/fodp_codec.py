"""
FODP codec — minimal Flat OpenDocument Presentation API.

ODF 1.3 Part 3, OASIS Royalty-Free Category 1.
Uses xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ODF namespace constants (ODF 1.3)
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
}

FODP_MIME = "application/vnd.oasis.opendocument.presentation-flat-xml"

# Maximum file size guard (64 MiB) — protects against large XML files
MAX_FILE_SIZE = 64 * 1024 * 1024


class FodpError(Exception):
    """Base exception for FODP codec errors."""


class FodpParseError(FodpError):
    """Raised when FODP parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse a FODP flat presentation file.

    The returned model contains:
        mime_type (str | None): office:mimetype attribute.
        is_fodp (bool): True if FODP MIME type.
        page_count (int): Number of draw:page elements.
        pages (list[dict]): Per-page data.
        styles_count (int): Number of style:style elements.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Parsed presentation model dict.

    Raises:
        FodpParseError: If source cannot be parsed.
        FodpError: For other load errors.
    """
    xml_bytes = _read_source(source)
    root = _parse_xml(xml_bytes)
    return _build_model(root)


def get_page_count(source: str | bytes | Path) -> int:
    """Return the number of slides/pages.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        Number of draw:page elements.
    """
    model = load(source)
    return model["page_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all text strings from all slides.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        List of non-empty text strings from all slides.
    """
    model = load(source)
    texts: list[str] = []
    for page in model.get("pages", []):
        texts.extend(page.get("text_content", []))
    return [t for t in texts if t]


def get_page_metadata(source: str | bytes | Path) -> list[dict[str, Any]]:
    """Return per-page metadata list.

    Each dict contains: name, style, master_page, title, text_content, shape_count.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        List of page metadata dicts.
    """
    model = load(source)
    return model.get("pages", [])


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
    elif isinstance(source, str):
        return source.encode("utf-8")
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise FodpError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise FodpError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise FodpParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FodpError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _parse_xml(xml_bytes: bytes) -> ET.Element:
    """Parse XML bytes safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise FodpParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a presentation model from the parsed XML root."""
    expected_tag = f"{{{NS['office']}}}document"
    if root.tag != expected_tag:
        raise FodpParseError(
            f"Root element must be office:document, got {root.tag!r}"
        )

    mime = root.get(f"{{{NS['office']}}}mimetype", "")
    pages = _extract_pages(root)
    styles = root.findall(f".//{{{NS['style']}}}style")

    return {
        "mime_type": mime,
        "is_fodp": mime == FODP_MIME,
        "page_count": len(pages),
        "pages": pages,
        "styles_count": len(styles),
    }


def _extract_pages(root: ET.Element) -> list[dict[str, Any]]:
    """Extract per-page metadata from all draw:page elements."""
    pages = []
    for page in root.iter(f"{{{NS['draw']}}}page"):
        page_info: dict[str, Any] = {
            "name": page.get(f"{{{NS['draw']}}}name", ""),
            "style": page.get(f"{{{NS['draw']}}}style-name", ""),
            "master_page": page.get(f"{{{NS['draw']}}}master-page-name", ""),
            "title": None,
            "text_content": [],
            "shape_count": 0,
        }
        for frame in page.iter(f"{{{NS['draw']}}}frame"):
            pres_class = frame.get(f"{{{NS['presentation']}}}class", "")
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
    return pages
