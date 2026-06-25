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
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "dc": "http://purl.org/dc/elements/1.1/",
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


def get_document_metadata(source: str | bytes | Path) -> dict[str, Any]:
    """Extract ODF document-level metadata from the ``<office:meta>`` element.

    Returns a dict with these keys (all ``str | None``):
        title, description, subject, creator, date, creation_date,
        generator, language, editing_cycles, editing_duration,
        initial_creator.

    Spec authority:
        ODF 1.3 Part 3, section 4 — Pre-defined metadata elements are stored
        in the ``<office:meta>`` element (FACT-FODP-EX-0103, FACT-FODP-EX-0107,
        FACT-FODP-EX-0109).

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Document metadata dict.

    Raises:
        FodpParseError: If source cannot be parsed.
    """
    xml_bytes = _read_source(source)
    root = _parse_xml(xml_bytes)

    expected_tag = f"{{{NS['office']}}}document"
    if root.tag != expected_tag:
        raise FodpParseError(
            f"Root element must be office:document, got {root.tag!r}"
        )

    return _extract_metadata(root)


get_document_metadata.spec_qname = "office:meta"  # type: ignore[attr-defined]


def export_to_txt(source: str | bytes | Path) -> str:
    """Export all slide text content as a plain-text string.

    Each text item is joined with a newline. Returns empty string if no text.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        Plain text string with all extracted text from all slides.
    """
    texts = extract_text(source)
    return "\n".join(texts)


def export_to_csv(source: str | bytes | Path) -> str:
    """Export slide metadata as a CSV string.

    Columns: slide_index, slide_name, shape_count, text_snippet (first 80 chars).
    Header row included.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        CSV string with slide data.
    """
    import io, csv as _csv
    model = load(source)
    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow(["slide_index", "slide_name", "shape_count", "text_snippet"])
    for i, page in enumerate(model.get("pages", [])):
        name = page.get("name", f"Slide {i + 1}")
        shape_count = page.get("shape_count", 0)
        texts = page.get("text_content", [])
        snippet = " ".join(texts)[:80]
        writer.writerow([i, name, shape_count, snippet])
    return buf.getvalue()


def export_to_json(source: str | bytes | Path) -> str:
    """Export the FODP model dict as a JSON string.

    Args:
        source: Path to .fodp file, bytes, or XML string.

    Returns:
        JSON string representation of the model.
    """
    import json
    return json.dumps(load(source), ensure_ascii=False)


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


def _extract_metadata(root: ET.Element) -> dict[str, Any]:
    """Extract pre-defined metadata from <office:meta>."""
    meta_el = root.find(f"{{{NS['office']}}}meta")
    # Map of result key -> (namespace_prefix, local_name)
    fields = {
        "title": ("dc", "title"),
        "description": ("dc", "description"),
        "subject": ("dc", "subject"),
        "creator": ("dc", "creator"),
        "date": ("dc", "date"),
        "language": ("dc", "language"),
        "creation_date": ("meta", "creation-date"),
        "generator": ("meta", "generator"),
        "editing_cycles": ("meta", "editing-cycles"),
        "editing_duration": ("meta", "editing-duration"),
        "initial_creator": ("meta", "initial-creator"),
    }
    result: dict[str, Any] = {}
    for key, (ns_prefix, local) in fields.items():
        if meta_el is not None:
            el = meta_el.find(f"{{{NS[ns_prefix]}}}{local}")
            result[key] = el.text if el is not None else None
        else:
            result[key] = None
    return result


# Analytics separation (TC-VNK-008 / decompose-monolithic-codec skill)
# Pure analytics functions are in presentation_document.py; re-exported here for backward compatibility.
try:
    from .presentation_document import *  # noqa: F401, F403
except ImportError:
    pass
