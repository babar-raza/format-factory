"""
FODG codec — minimal Flat OpenDocument Graphics API.

ODF 1.3 Part 3, OASIS Royalty-Free Category 1.
Uses xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from .exceptions import FodgError, FodgParseError

# ODF namespace constants (ODF 1.3)
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
}

FODG_MIME = "application/vnd.oasis.opendocument.graphics-flat-xml"

# Maximum file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024

# Shape element tags to count (direct children of draw:page)
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


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse a FODG flat graphics file.

    The returned model contains:
        mime_type (str | None): office:mimetype attribute.
        is_fodg (bool): True if FODG MIME type.
        page_count (int): Number of draw:page elements.
        pages (list[dict]): Per-page data.
        shapes_total (int): Total shape count across all pages.

    Args:
        source: Path to .fodg file, bytes, or XML string.

    Returns:
        Parsed graphics model dict.

    Raises:
        FodgParseError: If source cannot be parsed.
        FodgError: For other load errors.
    """
    xml_bytes = _read_source(source)
    root = _parse_xml(xml_bytes)
    return _build_model(root)


def get_shape_count(source: str | bytes | Path) -> int:
    """Return total shape count across all pages.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        Total number of shape elements.
    """
    model = load(source)
    return model["shapes_total"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all text strings from all pages.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        List of non-empty text strings from all pages.
    """
    model = load(source)
    texts: list[str] = []
    for page in model.get("pages", []):
        texts.extend(page.get("text_content", []))
    return [t for t in texts if t]


def get_page_metadata(source: str | bytes | Path) -> list[dict[str, Any]]:
    """Return per-page metadata list.

    Each dict contains: name, style, master_page, shape_count, text_content.

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
            raise FodgError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise FodgError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise FodgParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FodgError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _parse_xml(xml_bytes: bytes) -> ET.Element:
    """Parse XML bytes safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise FodgParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a graphics model from the parsed XML root."""
    expected_tag = f"{{{NS['office']}}}document"
    if root.tag != expected_tag:
        raise FodgParseError(
            f"Root element must be office:document, got {root.tag!r}"
        )

    mime = root.get(f"{{{NS['office']}}}mimetype", "")
    pages = _extract_pages(root)
    shapes_total = sum(p["shape_count"] for p in pages)

    return {
        "mime_type": mime,
        "is_fodg": mime == FODG_MIME,
        "page_count": len(pages),
        "pages": pages,
        "shapes_total": shapes_total,
    }


def _extract_pages(root: ET.Element) -> list[dict[str, Any]]:
    """Extract per-page metadata from all draw:page elements."""
    pages = []
    for page in root.iter(f"{{{NS['draw']}}}page"):
        page_info: dict[str, Any] = {
            "name": page.get(f"{{{NS['draw']}}}name", ""),
            "style": page.get(f"{{{NS['draw']}}}style-name", ""),
            "master_page": page.get(f"{{{NS['draw']}}}master-page-name", ""),
            "shape_count": 0,
            "shapes": [],
            "text_content": [],
        }
        # Count direct shape children (avoid double-counting shapes inside groups)
        for child in page:
            if child.tag in SHAPE_TAGS:
                page_info["shape_count"] += 1
        # Extract text from all text:p elements on the page
        for tp in page.iter(f"{{{NS['text']}}}p"):
            t = "".join(tp.itertext()).strip()
            if t:
                page_info["text_content"].append(t)
        pages.append(page_info)
    return pages


# ---------------------------------------------------------------------------
# Model creation and serialization (, R133-R136)
# ---------------------------------------------------------------------------

def create_fodg(pages_list: list[dict]) -> dict[str, Any]:
    """Create a minimal FODG graphics model from a list of page dicts.

    Args:
        pages_list: List of page dicts, each with optional:
                      'name' (str) — page name (default 'Page<n>').
                      'texts' (list[str]) — text content; each text becomes a shape.
                      'style' (str) — page style name.
                      'master_page' (str) — master page name.

    Returns:
        Graphics model dict compatible with write_fodg() and load().
    """
    pages = []
    for i, p in enumerate(pages_list):
        _raw_name = p.get("name")
        name = f"Page{i + 1}" if _raw_name is None else _raw_name
        texts = [str(t) for t in p.get("texts", []) if t is not None and str(t) != ""]
        page: dict[str, Any] = {
            "name": name,
            "shape_count": len(texts),
            "shapes": [],
            "text_content": texts,
            "style": p.get("style", ""),
            "master_page": p.get("master_page", ""),
        }
        pages.append(page)
    shapes_total = sum(p["shape_count"] for p in pages)
    return {
        "is_fodg": True,
        "mime_type": FODG_MIME,
        "page_count": len(pages),
        "pages": pages,
        "shapes_total": shapes_total,
    }


def write_fodg(model: dict[str, Any], dest: "str | Path") -> None:
    """Serialize a FODG model to a flat OpenDocument Graphics XML file.

    Args:
        model: Graphics model dict as returned by load() or create_fodg().
        dest:  Destination file path.

    Raises:
        FodgError: If model is not a valid FODG model dict or dest cannot be written.
    """
    if not isinstance(model, dict):
        raise FodgError("model must be a dict")
    if model.get("is_fodg") is False:
        raise FodgError("model is_fodg must be True")
    dest = Path(dest)
    root = ET.Element(f"{{{NS['office']}}}document")
    root.set(f"{{{NS['office']}}}mimetype", FODG_MIME)
    # Register namespaces to produce clean output
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    body = ET.SubElement(root, f"{{{NS['office']}}}body")
    drawing = ET.SubElement(body, f"{{{NS['office']}}}drawing")
    for page_data in model.get("pages", []):
        page_el = ET.SubElement(drawing, f"{{{NS['draw']}}}page")
        page_el.set(f"{{{NS['draw']}}}name", page_data.get("name", ""))
        for text in page_data.get("text_content", []):
            tb = ET.SubElement(page_el, f"{{{NS['draw']}}}text-box")
            tp = ET.SubElement(tb, f"{{{NS['text']}}}p")
            tp.text = text
    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    try:
        dest.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise FodgError(f"Cannot write {dest}: {exc}") from exc


def get_shapes(source: "str | bytes | Path") -> list[dict[str, Any]]:
    """Return a flat list of shape info dicts from all pages.

    Each dict contains: page_name, page_index, shape_index, tag (local name), text.

    Args:
        source: Path to .fodg file, bytes, or XML string.

    Returns:
        List of shape dicts; empty list if no shapes or on parse failure.
    """
    try:
        xml_bytes = _read_source(source)
        root = _parse_xml(xml_bytes)
    except (FodgError, ET.ParseError):
        return []
    shapes: list[dict[str, Any]] = []
    for page_idx, page in enumerate(root.iter(f"{{{NS['draw']}}}page")):
        page_name = page.get(f"{{{NS['draw']}}}name", "")
        shape_idx = 0
        for child in page:
            if child.tag in SHAPE_TAGS:
                # Extract text content from nested text:p elements
                text_parts = []
                for tp in child.iter(f"{{{NS['text']}}}p"):
                    text_parts.append("".join(tp.itertext()))
                text = "".join(text_parts)
                # Strip namespace from tag
                tag_name = child.tag.split("}", 1)[1] if "}" in child.tag else child.tag
                shapes.append({
                    "page_name": page_name,
                    "page_index": page_idx,
                    "shape_index": shape_idx,
                    "tag": tag_name,
                    "text": text,
                })
                shape_idx += 1
    return shapes


# ---------------------------------------------------------------------------
# Re-export extracted functions (TC-PA-017 monolith healing — pure refactor)
# ---------------------------------------------------------------------------
from .fodg_page_ops import *  # noqa: F401,F403,E402
