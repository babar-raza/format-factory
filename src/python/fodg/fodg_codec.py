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


class FodgError(Exception):
    """Base exception for FODG codec errors."""


class FodgParseError(FodgError):
    """Raised when FODG parsing fails."""


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
    except Exception:
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


def get_page_by_name(model: dict[str, Any], name: str) -> "dict[str, Any] | None":
    """Return the first page dict with matching name, or None if not found.

    Raises:
        TypeError: If model is not a dict or name is not a str.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    for page in model.get("pages", []):
        if page.get("name") == name:
            return page
    return None


# ---------------------------------------------------------------------------
# additions (R138) — add_page, get_text_shapes
# ---------------------------------------------------------------------------

def add_page(
    model: dict[str, Any], page_or_name: "str | dict"
) -> dict[str, Any]:
    """Return a new model with a page appended (immutable).

    Args:
        model: FODG graphics model dict.
        page_or_name: Either a str (page name) or a dict with optional 'name' and 'texts' keys.
                      If a str, an empty page with that name is added.
                      If a dict, 'texts' values become the page's text content / shapes.

    Raises:
        TypeError: If model is not a dict or page_or_name is not str or dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(page_or_name, (str, dict)):
        raise TypeError("page_or_name must be str or dict")
    pages = list(model.get("pages", []))
    auto_name = f"Page{len(pages) + 1}"
    if isinstance(page_or_name, str):
        name: str = page_or_name
        texts: list[str] = []
    else:
        name = page_or_name.get("name") or auto_name
        texts = [str(t) for t in page_or_name.get("texts", []) if t is not None]
    new_page: dict[str, Any] = {
        "name": name,
        "shape_count": len(texts),
        "shapes": [],
        "text_content": texts,
        "style": "",
        "master_page": "",
    }
    new_pages = pages + [new_page]
    shapes_total = sum(p.get("shape_count", 0) for p in new_pages)
    return {**model, "pages": new_pages, "page_count": len(new_pages), "shapes_total": shapes_total}


def get_text_shapes(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of page info dicts for pages that have non-empty text content.

    Each result dict contains: page_name, page_index, text_content (non-empty strings only).

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    result = []
    for idx, page in enumerate(model.get("pages", [])):
        texts = [t for t in page.get("text_content", []) if t]
        if texts:
            result.append({
                "page_name": page.get("name", ""),
                "page_index": idx,
                "text_content": texts,
            })
    return result


# ---------------------------------------------------------------------------
# additions (R140) — remove_page, rename_page
# ---------------------------------------------------------------------------

def remove_page(model: dict[str, Any], idx: int) -> dict[str, Any]:
    """Return a new model with the page at idx removed (immutable).

    Raises:
        TypeError: If model is not a dict.
        FodgError: If idx is out of range or negative.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if idx < 0 or idx >= len(pages):
        raise FodgError(
            f"page index {idx} out of range (0-{len(pages) - 1})"
        )
    new_pages = [p for i, p in enumerate(pages) if i != idx]
    shapes_total = sum(p.get("shape_count", 0) for p in new_pages)
    return {**model, "pages": new_pages, "page_count": len(new_pages), "shapes_total": shapes_total}


def rename_page(model: dict[str, Any], idx: int, name: str) -> dict[str, Any]:
    """Return a new model with the page at idx renamed (immutable).

    Raises:
        TypeError: If model is not a dict or name is not a str.
        FodgError: If idx is out of range or negative.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    pages = model.get("pages", [])
    if idx < 0 or idx >= len(pages):
        raise FodgError(f"page index {idx} out of range")
    new_pages = [
        ({**p, "name": name} if i == idx else p)
        for i, p in enumerate(pages)
    ]
    return {**model, "pages": new_pages}


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

def get_all_text(model: dict[str, Any]) -> list[str]:
    """Return a flat list of all non-empty text strings across all pages.

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    result: list[str] = []
    for page in model.get("pages", []):
        for t in page.get("text_content", []):
            if t:
                result.append(t)
    return result


def get_page_text(model: dict[str, Any], page_idx: int) -> list[str]:
    """Return a list of non-empty text strings from a specific page.

    Args:
        model: FODG neutral model dict.
        page_idx: Zero-based page index.

    Returns:
        List of non-empty text strings from the page. Empty list if page
        index is out of range or the page has no text.

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if page_idx < 0 or page_idx >= len(pages):
        return []
    return [t for t in pages[page_idx].get("text_content", []) if t]


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

def count_shapes(model: dict[str, Any]) -> int:
    """Return the total shape count across all pages."""
    return model.get("shapes_total", 0)


def export_to_json(model: dict[str, Any]) -> str:
    """Export a FODG model to a JSON string.

    Returns a JSON object with page_count, pages (name, shape_count, text_content),
    and shapes_total.
    """
    import json as _json
    out = {
        "page_count": model.get("page_count", 0),
        "pages": [
            {
                "name": p.get("name", ""),
                "shape_count": p.get("shape_count", 0),
                "text_content": p.get("text_content", []),
            }
            for p in model.get("pages", [])
        ],
        "shapes_total": model.get("shapes_total", 0),
    }
    return _json.dumps(out, ensure_ascii=True, indent=2)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

def duplicate_page(model: dict[str, Any], idx: int) -> dict[str, Any]:
    """Return a new model with a deep copy of the page at idx appended (immutable).

    Raises:
        TypeError: If model is not a dict.
        FodgError: If idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if idx < 0 or idx >= len(pages):
        raise FodgError(f"page index {idx} out of range")
    import copy as _copy
    page_copy = _copy.deepcopy(pages[idx])
    new_pages = list(pages) + [page_copy]
    shapes_total = sum(p.get("shape_count", 0) for p in new_pages)
    return {**model, "pages": new_pages, "page_count": len(new_pages), "shapes_total": shapes_total}


def get_page_index(model: dict[str, Any], name: str) -> int:
    """Return the zero-based index of the page with the given name.

    Raises:
        KeyError: If no page with that name exists.
    """
    for i, page in enumerate(model.get("pages", [])):
        if page.get("name") == name:
            return i
    raise KeyError(f"Page {name!r} not found")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

def clear_page(model: dict[str, Any], idx: int) -> dict[str, Any]:
    """Return a new model with all content cleared from the page at idx (immutable).

    Raises:
        TypeError: If model is not a dict.
        FodgError: If idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if idx < 0 or idx >= len(pages):
        raise FodgError(f"page index {idx} out of range")
    new_pages = [
        ({**p, "shape_count": 0, "shapes": [], "text_content": []} if i == idx else p)
        for i, p in enumerate(pages)
    ]
    shapes_total = sum(p.get("shape_count", 0) for p in new_pages)
    return {**model, "pages": new_pages, "shapes_total": shapes_total}


def swap_pages(model: dict[str, Any], idx1: int, idx2: int) -> dict[str, Any]:
    """Return a new model with the pages at idx1 and idx2 swapped (immutable).

    Raises:
        TypeError: If model is not a dict.
        FodgError: If either index is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    for idx in (idx1, idx2):
        if idx < 0 or idx >= len(pages):
            raise FodgError(f"page index {idx} out of range")
    new_pages = list(pages)
    new_pages[idx1], new_pages[idx2] = new_pages[idx2], new_pages[idx1]
    return {**model, "pages": new_pages}


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

def page_names(model: dict[str, Any]) -> list[str]:
    """Return a list of page names in order."""
    return [p.get("name", "") for p in model.get("pages", [])]


def has_page(model: dict[str, Any], name: str) -> bool:
    """Return True if any page has the given name (case-sensitive)."""
    return any(p.get("name") == name for p in model.get("pages", []))


# pfgi-rnext — get_page_count
# FORMAT_FACTORY_EXECUTION: taskcard=PFGI-TC-005; method=MANUAL_GOVERNED_BY_SKILL; skill=add-python-api; idempotency=3b38cde01bea7c6dc76227c9995d7389fcb0d420ce300d4652d1db576dc1d0b4; evidence=.local/evidences/product-first-governed-implementation-rnext/evidence-declaration.yaml
def get_page_count(model: dict[str, Any]) -> int:
    """Return the number of pages in the document.

    Args:
        model: FODG neutral model dict (must have 'pages' key).

    Returns:
        Integer count of pages. Returns 0 for empty or missing pages list.
    """
    return len(model.get("pages", []))


# pige-rnext — find_text
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-006; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=03d52c0a35f242d09916242da0014f343f8d9e0e9b27f5608d3e255d8d8c8117; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def find_text(model: dict[str, Any], query: str, *, case_sensitive: bool = True) -> list[dict]:
    """Search for text across all pages and return match locations.

    Args:
        model: FODG neutral model dict (must have 'pages' key).
        query: Text to search for.
        case_sensitive: Whether the search is case-sensitive. Default True.

    Returns:
        List of dicts with keys: page_index, page_name, shape_index, text.
    """
    results: list[dict] = []
    for pi, page in enumerate(model.get("pages", [])):
        page_name = page.get("name", f"Page {pi}")
        for si, shape in enumerate(page.get("shapes", [])):
            text = shape.get("text", "")
            if not text:
                continue
            match_text = text if case_sensitive else text.lower()
            match_query = query if case_sensitive else query.lower()
            if match_query in match_text:
                results.append({
                    "page_index": pi,
                    "page_name": page_name,
                    "shape_index": si,
                    "text": text,
                })
    return results


# ---------------------------------------------------------------------------
# Additional export / probe functions
# ---------------------------------------------------------------------------

def export_to_txt(source: "str | bytes | Path") -> str:
    """Export all text content from a FODG document to a plain text string.

    Each page is preceded by a header line: '=== PageName ===' or 'Page N' if unnamed.

    Args:
        source: Path to .fodg file, bytes, or XML string.

    Returns:
        Plain text string with page headers and texts joined by newlines.
    """
    model = load(source)
    sections: list[str] = []
    for page_idx, page in enumerate(model.get("pages", []), start=1):
        page_name = page.get("name", "")
        header = f"=== {page_name} ===" if page_name else f"Page {page_idx}"
        page_texts = [t for t in page.get("text_content", []) if t]
        sections.append(header)
        sections.extend(page_texts)
    return "\n".join(sections)


def probe_fodg(source: "str | bytes | Path") -> bool:
    """Probe whether source is a valid FODG document.

    Checks for the FODG MIME type without full parsing.
    Returns False on any error.

    Args:
        source: Path to a file, bytes, or XML string.

    Returns:
        True if source appears to be a FODG document, False otherwise.
    """
    try:
        xml_bytes = _read_source(source)
        snippet = xml_bytes[:4096].decode("utf-8", errors="replace")
        return FODG_MIME in snippet
    except Exception:
        return False


def export_to_csv(
    source: "str | bytes | Path",
    dest: "str | Path | None" = None,
) -> str:
    """Export FODG text content to a CSV string.

    Columns: page_name, shape_index, text. shape_index resets to 0 for each page.

    Args:
        source: Path to .fodg file, bytes, or XML string.
        dest:   Optional destination path; if given, CSV is also written there.

    Returns:
        CSV string with header 'page_name,shape_index,text'.
    """

    def _csv_field(value: str) -> str:
        if "," in value or '"' in value or "\n" in value:
            return '"' + value.replace('"', '""') + '"'
        return value

    model = load(source)
    lines = ["page_name,shape_index,text"]
    for page in model.get("pages", []):
        page_name = page.get("name", "")
        for shape_idx, text in enumerate(page.get("text_content", [])):
            lines.append(f"{_csv_field(page_name)},{shape_idx},{_csv_field(text)}")
    csv_str = "\n".join(lines) + "\n"
    if dest is not None:
        dest_path = Path(dest)
        try:
            dest_path.write_text(csv_str, encoding="utf-8")
        except OSError as exc:
            raise FodgError(f"Cannot write {dest_path}: {exc}") from exc
    return csv_str


def roundtrip(
    source: "str | bytes | Path",
    dest: "str | Path",
) -> dict:
    """Load a FODG document, write it to dest, then reload and return the model.

    Args:
        source: Path to source .fodg file or raw bytes.
        dest:   Destination path for the roundtripped file.

    Returns:
        The reloaded FODG model dict.
    """
    model = load(source)
    write_fodg(model, dest)
    return load(dest)


def total_text_length(model: dict[str, Any]) -> int:
    """Return the total character count of all text across all pages.

    Sums the length of every text string extracted from all pages.

    Args:
        model: FODG model dict.

    Returns:
        Total number of characters in all text content.
    """
    return sum(len(t) for t in get_all_text(model))


def find_shapes_by_text_pattern(model: dict[str, Any], pattern: str) -> list[dict[str, Any]]:
    """Find shapes across all pages whose text matches a regex pattern.

    Args:
        model: FODG model dict.
        pattern: Regular expression pattern to search for.

    Returns:
        List of dicts with keys: page_idx, shape_idx, text, matched.
        Returns [] for no matches or invalid pattern.
    """
    import re
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    try:
        compiled = re.compile(pattern)
    except re.error:
        return []

    results = []
    pages = model.get("pages", [])
    for page_idx, page in enumerate(pages):
        texts = page.get("text_content", [])
        for shape_idx, text in enumerate(texts):
            if text and compiled.search(text):
                results.append({
                    "page_idx": page_idx,
                    "shape_idx": shape_idx,
                    "text": text,
                    "matched": True,
                })
    return results


def export_page_to_json(model: dict[str, Any], page_idx: int) -> str:
    """Export a single page as a JSON string.

    Args:
        model: FODG model dict.
        page_idx: Zero-based page index.

    Returns:
        JSON string representing the page, or '{}' if page_idx out of range.
    """
    import json
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if page_idx < 0 or page_idx >= len(pages):
        return "{}"
    page = pages[page_idx]
    return json.dumps(page, ensure_ascii=False)


# Analytics domain functions are in drawing_document.py (TC-ANAL-SEG-HEAL-001, 2026-06-22).

