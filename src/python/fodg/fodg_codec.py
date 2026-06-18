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
# Model creation and serialization (Sprint 4, R133-R136)
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
# Sprint 5 additions (R138) — add_page, get_text_shapes
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
# Sprint 6 additions (R140) — remove_page, rename_page
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
# Sprint 7 additions (R142)
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
# Sprint 8 additions (R144)
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
# Sprint 9 additions (R146)
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
# Sprint 10 additions (R148)
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
# Sprint 11 additions (R150)
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


def fodg_total_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of shapes across all pages in a FODG file.

    Args:
        file_path: Path to a FODG file.

    Returns:
        Integer total shape count across all pages.

    Raises:
        FodgError subclasses on parse failure.
    """
    model = load(file_path)
    return get_shape_count(file_path)


def fodg_text_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of text shapes across all pages in a FODG file.

    Args:
        file_path: Path to a FODG file.

    Returns:
        Integer count of text shapes. Returns 0 if no text shapes exist.

    Raises:
        FodgError subclasses on parse failure.
    """
    model = load(file_path)
    return len(get_text_shapes(model))


def fodg_page_shape_count(model: dict[str, Any], page_idx: int) -> int:
    """Return the number of shapes on a specific page.

    Uses the shape_count field from the parsed model when available,
    falling back to the length of the shapes list.

    Args:
        model: FODG model dict returned by load().
        page_idx: Zero-based index of the page.

    Returns:
        Integer count of shapes on the page. Returns 0 if page_idx is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    pages = model.get("pages", [])
    if page_idx < 0 or page_idx >= len(pages):
        return 0
    page = pages[page_idx]
    if "shape_count" in page:
        return int(page["shape_count"])
    return len(page.get("shapes", []))


def fodg_avg_shapes_per_page(file_path: "str | bytes | Path") -> float:
    """Return the average number of shapes per page.

    Args:
        file_path: Path to a .fodg file.

    Returns:
        Float average shape count per page, or 0.0 if no pages.
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = sum(p.get("shape_count", 0) for p in pages)
    return total / len(pages)


def fodg_has_empty_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if any page contains zero shapes.

    Args:
        file_path: Path to a .fodg file.

    Returns:
        True if at least one page has no shapes, False otherwise.
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return any(p.get("shape_count", 0) == 0 for p in pages)


def fodg_page_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of pages in the FODG document."""
    doc = load(file_path)
    return len(doc.get("pages", []))


def fodg_all_pages_have_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if every page has at least one shape; False otherwise."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return False
    return all(p.get("shape_count", 0) > 0 for p in pages)


def fodg_text_to_shape_ratio(file_path: "str | bytes | Path") -> float:
    """Return the ratio of text shapes to total shapes. 0.0 if no shapes."""
    total = get_shape_count(file_path)
    if total == 0:
        return 0.0
    doc = load(file_path)
    text_count = len(get_text_shapes(doc))
    return text_count / total


def fodg_max_shapes_per_page(file_path: "str | bytes | Path") -> int:
    """Return the maximum number of shapes on any single page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return max(p.get("shape_count", 0) for p in pages)


def fodg_min_shapes_per_page(file_path: "str | bytes | Path") -> int:
    """Return the minimum number of shapes on any single page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return min(p.get("shape_count", 0) for p in pages)


def fodg_shape_density(file_path: "str | bytes | Path") -> float:
    """Return total shapes / page count. 0.0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = sum(p.get("shape_count", 0) for p in pages)
    return total / len(pages)


def fodg_empty_page_count(file_path: "str | bytes | Path") -> int:
    """Return the number of pages with zero shapes."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages if p.get("shape_count", 0) == 0)


def fodg_is_single_page(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has exactly one page."""
    doc = load(file_path)
    return len(doc.get("pages", [])) == 1


def fodg_total_text_length(file_path: "str | bytes | Path") -> int:
    """Return total character count of all text content in the drawing."""
    doc = load(file_path)
    total = 0
    for page in doc.get("pages", []):
        for shape in page.get("shapes", []):
            total += len(shape.get("text", ""))
    return total


def fodg_has_text(file_path: "str | bytes | Path") -> bool:
    """Return True if any shape in the drawing contains text."""
    return fodg_total_text_length(file_path) > 0


def fodg_is_empty_document(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has no shapes on any page."""
    return fodg_total_shape_count(file_path) == 0


def fodg_non_text_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the count of shapes that are not text shapes."""
    return fodg_total_shape_count(file_path) - fodg_text_shape_count(file_path)


def fodg_avg_text_per_page(file_path: "str | bytes | Path") -> float:
    """Return average character count of text per page. 0.0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = fodg_total_text_length(file_path)
    return total / len(pages)


def fodg_has_multiple_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has more than one page."""
    return fodg_page_count(file_path) > 1


def fodg_shape_to_page_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of shape counts across pages. 0.0 if fewer than 2 pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if len(pages) < 2:
        return 0.0
    counts = [p.get("shape_count", 0) for p in pages]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fodg_max_text_per_page(file_path: "str | bytes | Path") -> int:
    """Return the maximum text length on any single page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    lengths = [sum(len(t) for t in p.get("text_content", [])) for p in pages]
    return max(lengths) if lengths else 0


def fodg_text_per_shape(file_path: "str | bytes | Path") -> float:
    """Return total text length / total shapes. 0.0 if no shapes."""
    shapes = fodg_total_shape_count(file_path)
    if shapes == 0:
        return 0.0
    return fodg_total_text_length(file_path) / shapes


def fodg_nonempty_page_count(file_path: "str | bytes | Path") -> int:
    """Return the count of pages that have at least one shape."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages if p.get("shape_count", 0) > 0)


def fodg_text_density(file_path: "str | bytes | Path") -> float:
    """Return total text length / total shape count. 0.0 if no shapes."""
    total_shapes = fodg_total_shape_count(file_path)
    if total_shapes == 0:
        return 0.0
    return fodg_total_text_length(file_path) / total_shapes


def fodg_is_multi_page(file_path: "str | bytes | Path") -> bool:
    """Return True if document has more than one page."""
    return fodg_page_count(file_path) > 1


def fodg_shape_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of shape counts across pages. 0.0 if fewer than 2 pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if len(pages) < 2:
        return 0.0
    counts = [len(p.get("shapes", [])) for p in pages]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fodg_is_text_only(file_path: "str | bytes | Path") -> bool:
    """Return True if all shapes are text shapes (text_shape_count == total_shape_count)."""
    total = fodg_total_shape_count(file_path)
    if total == 0:
        return False
    return fodg_text_shape_count(file_path) == total


def fodg_avg_shapes_per_nonempty_page(file_path: "str | bytes | Path") -> float:
    """Return average shape count per non-empty page. 0.0 if no non-empty pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    nonempty = [p.get("shape_count", 0) for p in pages if p.get("shape_count", 0) > 0]
    if not nonempty:
        return 0.0
    return sum(nonempty) / len(nonempty)


def fodg_has_single_shape(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains exactly one shape across all pages."""
    return fodg_total_shape_count(file_path) == 1


def fodg_page_text_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of text lengths across pages. 0.0 if fewer than 2 pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if len(pages) < 2:
        return 0.0
    lengths = []
    for p in pages:
        text = ""
        for s in p.get("shapes", []):
            text += s.get("text", "")
        lengths.append(len(text))
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def fodg_total_text_chars(file_path: "str | bytes | Path") -> int:
    """Return total character count of all text in all shapes across all pages."""
    doc = load(file_path)
    total = 0
    for p in doc.get("pages", []):
        for s in p.get("shapes", []):
            total += len(s.get("text", ""))
    return total


def fodg_avg_text_per_shape(file_path: "str | bytes | Path") -> float:
    """Return average text length per shape. 0.0 if no shapes."""
    doc = load(file_path)
    lengths = []
    for p in doc.get("pages", []):
        for s in p.get("shapes", []):
            lengths.append(len(s.get("text", "")))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def fodg_min_text_per_page(file_path: "str | bytes | Path") -> int:
    """Return the minimum total text length of any page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    page_lens = []
    for p in pages:
        total = sum(len(s.get("text", "")) for s in p.get("shapes", []))
        page_lens.append(total)
    return min(page_lens)


def fodg_total_text_items(file_path: "str | bytes | Path") -> int:
    """Return total count of text content items across all pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(len(pg.get("text_content", [])) for pg in pages)


def fodg_avg_shapes_per_page(file_path: "str | bytes | Path") -> float:
    """Return average shape count per page. 0.0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    return sum(pg.get("shape_count", 0) for pg in pages) / len(pages)


def fodg_nonempty_shape_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of shapes with non-empty text to total shapes. 0.0 if no shapes."""
    doc = load(file_path)
    all_shapes = [s for p in doc.get("pages", []) for s in p.get("shapes", [])]
    if not all_shapes:
        return 0.0
    nonempty = sum(1 for s in all_shapes if s.get("text", "").strip())
    return nonempty / len(all_shapes)


def fodg_max_shape_text_length(file_path: "str | bytes | Path") -> int:
    """Return length of text in the shape with the most text. 0 if no shapes."""
    doc = load(file_path)
    lengths = [
        len(s.get("text", ""))
        for p in doc.get("pages", [])
        for s in p.get("shapes", [])
    ]
    return max(lengths) if lengths else 0


def fodg_shapes_with_text_count(file_path: "str | bytes | Path") -> int:
    """Return count of shapes that have non-empty text content."""
    doc = load(file_path)
    return sum(
        1 for p in doc.get("pages", [])
        for s in p.get("shapes", [])
        if s.get("text", "").strip()
    )


def fodg_nonempty_page_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of pages with at least one shape to total pages. 0.0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    nonempty = sum(1 for p in pages if p.get("shapes") or p.get("shape_count", 0) > 0)
    return nonempty / len(pages)


def fodg_total_shapes_and_pages(file_path: "str | bytes | Path") -> int:
    """Return combined count of total shapes plus total pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    return total_shapes + len(pages)


def fodg_has_non_text_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if any page contains at least one non-text shape."""
    return fodg_non_text_shape_count(file_path) > 0


def fodg_has_no_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains no shapes on any page."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(p.get("shape_count", 0) for p in pages) == 0


def fodg_all_pages_have_text(file_path: "str | bytes | Path") -> bool:
    """Return True if every page has at least one non-empty text content item.

    Args:
        file_path: Path to the .fodg file.

    Returns:
        True if all pages have non-empty text; False if any page has no text or doc is empty.
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return False
    return all(
        any(t.strip() for t in p.get("text_content", []))
        for p in pages
    )


def fodg_max_text_item_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the longest text item across all pages. 0 if no text.

    Args:
        file_path: Path to the .fodg file.

    Returns:
        Maximum text item character length as int; 0 if no text content found.
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return max(lengths) if lengths else 0


def fodg_file_size_bytes(file_path: "str | bytes | Path") -> int:
    """Return the file size in bytes."""
    from pathlib import Path as _Path
    return _Path(file_path).stat().st_size


def fodg_min_text_item_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the shortest non-empty text item across all pages. 0 if none."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return min(lengths) if lengths else 0


def fodg_avg_text_item_length(file_path: "str | bytes | Path") -> float:
    """Return average length of text items across all pages. 0.0 if none."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return sum(lengths) / len(lengths) if lengths else 0.0


def fodg_unique_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return count of distinct non-empty text items across all pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    texts = {t.strip() for p in pages for t in p.get("text_content", []) if t.strip()}
    return len(texts)


def fodg_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return total count of non-empty text items across all pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages for t in p.get("text_content", []) if t.strip())


def fodg_shape_density(file_path: "str | bytes | Path") -> float:
    """Return shapes per page. 0.0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = sum(p.get("shape_count", 0) for p in pages)
    return total / len(pages)


def fodg_has_text_content(file_path: "str | bytes | Path") -> bool:
    """Return True if any page has non-empty text content."""
    doc = load(file_path)
    for p in doc.get("pages", []):
        for t in p.get("text_content", []):
            if t.strip():
                return True
    return False


def fodg_max_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum shape count on any single page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return max(p.get("shape_count", 0) for p in pages)


def fodg_min_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum shape count on any single page. 0 if no pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return min(p.get("shape_count", 0) for p in pages)


def fodg_is_empty_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has no shapes on any page."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    return all(p.get("shape_count", 0) == 0 for p in pages)


def fodg_has_multiple_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing contains more than one shape in total."""
    return fodg_total_shape_count(file_path) > 1


def fodg_shapes_exceed_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count exceeds the number of pages."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    return total_shapes > len(pages)


def fodg_word_count(file_path: "str | bytes | Path") -> int:
    """Return total word count across all text items in the drawing."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    total = 0
    for page in pages:
        for item in page.get("text_items", []):
            total += len(item.split())
    return total


def fodg_shape_text_ratio(file_path: "str | bytes | Path") -> float:
    """Return the ratio of shapes with text to total shapes. 0.0 if no shapes."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    if total_shapes == 0:
        return 0.0
    text_count = sum(len(p.get("text_items", [])) for p in pages)
    return min(1.0, text_count / total_shapes)


def fodg_unique_word_count(file_path: "str | bytes | Path") -> int:
    """Return the number of unique words across all text items."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    words = set()
    for page in pages:
        for item in page.get("text_items", []):
            words.update(item.lower().split())
    return len(words)


def fodg_text_and_shape_sum(file_path: "str | bytes | Path") -> int:
    """Return sum of text item count and total shape count."""
    return fodg_text_item_count(file_path) + fodg_total_shape_count(file_path)


def fodg_text_items_exceed_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count strictly exceeds page count."""
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)


def fodg_text_item_length_range(file_path: "str | bytes | Path") -> int:
    """Return range (max minus min) of text item lengths. 0 if fewer than 2 items."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    if len(lengths) < 2:
        return 0
    return max(lengths) - min(lengths)


def fodg_text_items_per_shape(file_path: "str | bytes | Path") -> float:
    """Return average text items per shape. 0.0 if no shapes."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    if total_shapes == 0:
        return 0.0
    text_items = sum(len(p.get("text_content", [])) for p in pages)
    return text_items / total_shapes


def fodg_shape_count_exceeds_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count."""
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)






def fodg_has_equal_shapes_and_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count."""
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)




def fodg_shape_count_equals_page_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals page count."""
    return fodg_total_shape_count(file_path) == fodg_page_count(file_path)




def fodg_non_text_shape_count_exceeds_page_count(file_path: "str | bytes | Path") -> bool:
    """Return True if non-text shape count strictly exceeds page count."""
    return fodg_non_text_shape_count(file_path) > fodg_page_count(file_path)


def fodg_text_item_length_sum(file_path: "str | bytes | Path") -> int:
    """Return sum of character lengths of all text_content items across all pages. 0 if none."""
    doc = load(file_path)
    return sum(len(t) for p in doc.get("pages", []) for t in p.get("text_content", []))


def fodg_shape_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by 2."""
    doc = load(file_path)
    total = sum(p.get("shape_count", 0) for p in doc.get("pages", []))
    return total * 2


def fodg_shape_count_times_text_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by total text item count. 0 if either is 0."""
    doc = load(file_path)
    pages = doc.get("pages", [])
    shapes = sum(p.get("shape_count", 0) for p in pages)
    texts = sum(len(p.get("text_content", [])) for p in pages)
    return shapes * texts




def fodg_text_item_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the text item count multiplied by two."""
    return fodg_text_item_count(file_path) * 2


def fodg_has_more_shapes_than_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count."""
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)






def fodg_file_size_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes multiplied by total page count."""
    return fodg_file_size_bytes(file_path) * fodg_page_count(file_path)


def fodg_text_item_count_squared(file_path: "str | bytes | Path") -> int:
    """Return total text item count squared (multiplied by itself)."""
    tc = fodg_text_item_count(file_path)
    return tc * tc






def fodg_text_item_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the text item count multiplied by three."""
    return fodg_text_item_count(file_path) * 3


def fodg_has_exactly_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly one."""
    return fodg_text_item_count(file_path) == 1




def fodg_shape_count_times_text_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count * text item count * page count."""
    return fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * fodg_page_count(file_path)


def fodg_total_shape_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by two."""
    return fodg_total_shape_count(file_path) * 2


def fodg_has_no_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are no text items in the document."""
    return fodg_text_item_count(file_path) == 0






def fodg_max_shapes_per_page_times_two(file_path: "str | bytes | Path") -> int:
    """Return the maximum shapes per page multiplied by two."""
    return fodg_max_shapes_per_page(file_path) * 2


def fodg_has_at_least_two_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is at least two."""
    return fodg_total_shape_count(file_path) >= 2


def fodg_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by three."""
    return fodg_total_shape_count(file_path) * 3


def fodg_has_no_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if there are no shapes in the document."""
    return fodg_total_shape_count(file_path) == 0




def fodg_has_exactly_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is exactly three."""
    return fodg_total_shape_count(file_path) == 3




def fodg_has_exactly_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is exactly two."""
    return fodg_text_item_count(file_path) == 2




def fodg_has_at_least_one_text_item(file_path: "str | bytes | Path") -> bool:
    """Return True if there is at least one text item."""
    return fodg_text_item_count(file_path) >= 1




def fodg_has_more_text_than_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count strictly exceeds page count."""
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)




def fodg_has_equal_shapes_and_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count."""
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)




def fodg_has_more_shapes_than_text(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count strictly exceeds text item count."""
    return fodg_total_shape_count(file_path) > fodg_text_item_count(file_path)


def fodg_total_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the total shape count."""
    n = fodg_total_shape_count(file_path)
    return n * n


def fodg_has_at_least_two_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if there are at least two text items."""
    return fodg_text_item_count(file_path) >= 2




def fodg_is_empty_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has no shapes and no text items."""
    return fodg_total_shape_count(file_path) == 0 and fodg_text_item_count(file_path) == 0


def fodg_page_count_times_shape_count(file_path: "str | bytes | Path") -> int:
    """Return page count multiplied by total shape count."""
    return fodg_page_count(file_path) * fodg_total_shape_count(file_path)


def fodg_has_only_one_shape(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has exactly one shape across all pages."""
    return fodg_total_shape_count(file_path) == 1


def fodg_text_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return text item count multiplied by page count."""
    return fodg_text_item_count(file_path) * fodg_page_count(file_path)


def fodg_has_more_pages_than_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if page count exceeds total shape count."""
    return fodg_page_count(file_path) > fodg_total_shape_count(file_path)




def fodg_has_at_least_three_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if drawing has at least three shapes across all pages."""
    return fodg_total_shape_count(file_path) >= 3


def fodg_text_count_times_shape_count(file_path: "str | bytes | Path") -> int:
    """Return text item count multiplied by total shape count."""
    return fodg_text_item_count(file_path) * fodg_total_shape_count(file_path)


def fodg_is_single_shape_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has exactly one shape."""
    return fodg_total_shape_count(file_path) == 1




def fodg_page_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count."""
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)




def fodg_has_zero_text_items(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has no text items."""
    return fodg_text_item_count(file_path) == 0




def fodg_text_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals shape count."""
    return fodg_text_item_count(file_path) == fodg_total_shape_count(file_path)




def fodg_shape_count_is_even(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is even."""
    return fodg_total_shape_count(file_path) % 2 == 0


def fodg_shape_count_times_page_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return shape_count * page_count * 2."""
    return fodg_total_shape_count(file_path) * fodg_page_count(file_path) * 2


def fodg_text_count_is_positive(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is greater than zero."""
    return fodg_text_item_count(file_path) > 0




def fodg_shape_count_is_three(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals 3."""
    return fodg_total_shape_count(file_path) == 3




def fodg_text_count_is_two(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals 2."""
    return fodg_text_item_count(file_path) == 2


def fodg_shape_count_times_text_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return shape_count * text_count * 2."""
    return fodg_total_shape_count(file_path) * fodg_text_item_count(file_path) * 2


def fodg_shape_count_is_zero(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals zero."""
    return fodg_total_shape_count(file_path) == 0




def fodg_page_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals text item count."""
    return fodg_page_count(file_path) == fodg_text_item_count(file_path)




def fodg_text_count_less_than_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is strictly less than shape count."""
    return fodg_text_item_count(file_path) < fodg_total_shape_count(file_path)




def fodg_text_count_is_zero(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count equals zero."""
    return fodg_text_item_count(file_path) == 0




def fodg_shape_count_is_one(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals one."""
    return fodg_total_shape_count(file_path) == 1




def fodg_page_count_greater_than_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count is strictly greater than text item count."""
    return fodg_page_count(file_path) > fodg_text_item_count(file_path)



def fodg_shape_count_greater_than_one(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is strictly greater than one."""
    return fodg_total_shape_count(file_path) > 1


def fodg_page_count_equals_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if page count equals total shape count."""
    return fodg_page_count(file_path) == fodg_total_shape_count(file_path)


def fodg_shape_count_equals_text_count(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count equals text item count."""
    return fodg_total_shape_count(file_path) == fodg_text_item_count(file_path)

def fodg_text_count_squared(file_path: "str | bytes | Path") -> int:
    """Return text item count squared."""
    tc = fodg_text_item_count(file_path)
    return tc * tc

def fodg_text_count_not_equal_shape_count(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is not equal to total shape count."""
    return fodg_text_item_count(file_path) != fodg_total_shape_count(file_path)

def fodg_shape_count_cubed(file_path: "str | bytes | Path") -> int:
    """Return total shape count cubed."""
    sc = fodg_total_shape_count(file_path)
    return sc * sc * sc

def fodg_shape_count_is_odd(file_path: "str | bytes | Path") -> bool:
    """Return True if total shape count is odd."""
    return fodg_total_shape_count(file_path) % 2 == 1

def fodg_text_count_cubed(file_path: "str | bytes | Path") -> int:
    """Return text item count cubed."""
    tc = fodg_text_item_count(file_path)
    return tc * tc * tc

def fodg_text_count_is_even(file_path: "str | bytes | Path") -> bool:
    """Return True if text item count is even."""
    return fodg_text_item_count(file_path) % 2 == 0

def fodg_text_count_less_than_page_count(file_path):
    return fodg_text_item_count(file_path) < fodg_page_count(file_path)
def fodg_shape_count_not_equal_text_count(file_path):
    return fodg_total_shape_count(file_path) != fodg_text_item_count(file_path)
def fodg_page_count_greater_than_shape_count(file_path):
    return fodg_page_count(file_path) > fodg_total_shape_count(file_path)
def fodg_text_count_greater_than_page_count(file_path):
    return fodg_text_item_count(file_path) > fodg_page_count(file_path)

































def fodg_page_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the page count."""
    pc = fodg_page_count(file_path)
    return pc * pc














def fodg_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the total shape count."""
    sc = fodg_total_shape_count(file_path)
    return sc * sc
















def fodg_total_shape_count_times_page_count(file_path: "str | bytes | Path") -> int:
    """Return total shape count times page count."""
    return fodg_total_shape_count(file_path) * fodg_page_count(file_path)






























def fodg_file_size_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the file size in bytes."""
    fs = fodg_file_size_bytes(file_path)
    return fs * fs


def fodg_page_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the page count multiplied by three."""
    return fodg_page_count(file_path) * 3




def fodg_text_count_times_page_count_squared(file_path: "str | bytes | Path") -> int:
    """Return text_item_count * page_count^2."""
    return fodg_text_item_count(file_path) * (fodg_page_count(file_path) ** 2)


def fodg_page_count_times_two(file_path: "str | bytes | Path") -> int:
    """Return the page count multiplied by two."""
    return fodg_page_count(file_path) * 2


























def fodg_total_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    """Return the total shape count multiplied by three."""
    return fodg_total_shape_count(file_path) * 3


def fodg_max_shapes_per_page_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the max shapes per page."""
    ms = fodg_max_shapes_per_page(file_path)
    return ms * ms


def fodg_non_text_shape_count_squared(file_path: "str | bytes | Path") -> int:
    """Return the square of the non-text shape count."""
    nt = fodg_non_text_shape_count(file_path)
    return nt * nt


def fodg_file_size_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_file_size_bytes(file_path) * 3


def fodg_total_text_items_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_total_text_items(file_path) * 3


def fodg_max_shapes_per_page_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_max_shapes_per_page(file_path) * 3


def fodg_non_text_shape_count_times_three(file_path: "str | bytes | Path") -> int:
    return fodg_non_text_shape_count(file_path) * 3


def fodg_file_size_times_four(file_path: "str | bytes | Path") -> int:
    return fodg_file_size_bytes(file_path) * 4


def fodg_total_text_items_times_four(file_path: "str | bytes | Path") -> int:
    return fodg_total_text_items(file_path) * 4


def fodg_page_count_times_four(file_path: "str | bytes | Path") -> int:
    """Return page count multiplied by four."""
    return fodg_page_count(file_path) * 4


def fodg_total_shape_count_times_four(file_path: "str | bytes | Path") -> int:
    """Return total shape count multiplied by four."""
    return fodg_total_shape_count(file_path) * 4


def fodg_page_count_times_five(file_path: "str | Path") -> int:
    """Return page count multiplied by five."""
    return fodg_page_count(file_path) * 5


def fodg_total_shape_count_times_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by five."""
    return fodg_total_shape_count(file_path) * 5


def fodg_page_count_times_six(file_path: "str | Path") -> int:
    """Return page count multiplied by six."""
    return fodg_page_count(file_path) * 6


def fodg_total_shape_count_times_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by six."""
    return fodg_total_shape_count(file_path) * 6


def fodg_page_count_times_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by seven."""
    return fodg_page_count(file_path) * 7


def fodg_total_shape_count_times_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seven."""
    return fodg_total_shape_count(file_path) * 7


def fodg_page_count_times_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by eight."""
    return fodg_page_count(file_path) * 8


def fodg_total_shape_count_times_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eight."""
    return fodg_total_shape_count(file_path) * 8


def fodg_page_count_times_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by nine."""
    return fodg_page_count(file_path) * 9


def fodg_total_shape_count_times_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by nine."""
    return fodg_total_shape_count(file_path) * 9


def fodg_page_count_times_ten(file_path: "str | Path") -> int:
    """Return page count multiplied by ten."""
    return fodg_page_count(file_path) * 10


def fodg_total_shape_count_times_ten(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ten."""
    return fodg_total_shape_count(file_path) * 10


def fodg_page_count_times_eleven(file_path: "str | Path") -> int:
    """Return page count multiplied by eleven."""
    return fodg_page_count(file_path) * 11


def fodg_total_shape_count_times_eleven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eleven."""
    return fodg_total_shape_count(file_path) * 11


def fodg_page_count_times_twelve(file_path: "str | Path") -> int:
    """Return page count multiplied by twelve."""
    return fodg_page_count(file_path) * 12


def fodg_total_shape_count_times_twelve(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twelve."""
    return fodg_total_shape_count(file_path) * 12


def fodg_page_count_times_thirteen(file_path: "str | Path") -> int:
    """Return page count multiplied by thirteen."""
    return fodg_page_count(file_path) * 13


def fodg_total_shape_count_times_thirteen(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirteen."""
    return fodg_total_shape_count(file_path) * 13


def fodg_page_count_times_fourteen(file_path):
    """Return page count multiplied by fourteen."""
    return fodg_page_count(file_path) * 14


def fodg_total_shape_count_times_fourteen(file_path):
    """Return total shape count multiplied by fourteen."""
    return fodg_total_shape_count(file_path) * 14


def fodg_page_count_times_fifteen(file_path):
    """Return page count multiplied by fifteen."""
    return fodg_page_count(file_path) * 15


def fodg_total_shape_count_times_fifteen(file_path):
    """Return total shape count multiplied by fifteen."""
    return fodg_total_shape_count(file_path) * 15


def fodg_page_count_times_sixteen(file_path):
    """Return page count multiplied by sixteen."""
    return fodg_page_count(file_path) * 16


def fodg_total_shape_count_times_sixteen(file_path):
    """Return total shape count multiplied by sixteen."""
    return fodg_total_shape_count(file_path) * 16


def fodg_page_count_times_seventeen(file_path):
    """Return page count multiplied by seventeen."""
    return fodg_page_count(file_path) * 17


def fodg_total_shape_count_times_seventeen(file_path):
    """Return total shape count multiplied by seventeen."""
    return fodg_total_shape_count(file_path) * 17


def fodg_page_count_times_eighteen(file_path):
    """Return page count multiplied by eighteen."""
    return fodg_page_count(file_path) * 18


def fodg_total_shape_count_times_eighteen(file_path):
    """Return total shape count multiplied by eighteen."""
    return fodg_total_shape_count(file_path) * 18


def fodg_page_count_times_nineteen(file_path):
    """Return page count multiplied by nineteen."""
    return fodg_page_count(file_path) * 19


def fodg_total_shape_count_times_nineteen(file_path):
    """Return total shape count multiplied by nineteen."""
    return fodg_total_shape_count(file_path) * 19


def fodg_page_count_times_twenty(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty."""
    return fodg_page_count(file_path) * 20


def fodg_total_shape_count_times_twenty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty."""
    return fodg_total_shape_count(file_path) * 20


def fodg_page_count_times_twenty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-one."""
    return fodg_page_count(file_path) * 21


def fodg_total_shape_count_times_twenty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-one."""
    return fodg_total_shape_count(file_path) * 21


def fodg_page_count_times_twenty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-two."""
    return fodg_page_count(file_path) * 22


def fodg_total_shape_count_times_twenty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-two."""
    return fodg_total_shape_count(file_path) * 22


def fodg_page_count_times_twenty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-three."""
    return fodg_page_count(file_path) * 23


def fodg_total_shape_count_times_twenty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-three."""
    return fodg_total_shape_count(file_path) * 23


def fodg_page_count_times_twenty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-four."""
    return fodg_page_count(file_path) * 24


def fodg_total_shape_count_times_twenty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-four."""
    return fodg_total_shape_count(file_path) * 24


def fodg_page_count_times_twenty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-five."""
    return fodg_page_count(file_path) * 25


def fodg_total_shape_count_times_twenty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-five."""
    return fodg_total_shape_count(file_path) * 25


def fodg_page_count_times_twenty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-six."""
    return fodg_page_count(file_path) * 26


def fodg_total_shape_count_times_twenty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-six."""
    return fodg_total_shape_count(file_path) * 26


def fodg_page_count_times_twenty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-seven."""
    return fodg_page_count(file_path) * 27


def fodg_total_shape_count_times_twenty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-seven."""
    return fodg_total_shape_count(file_path) * 27


def fodg_page_count_times_twenty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-eight."""
    return fodg_page_count(file_path) * 28


def fodg_total_shape_count_times_twenty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-eight."""
    return fodg_total_shape_count(file_path) * 28


def fodg_page_count_times_twenty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by twenty-nine."""
    return fodg_page_count(file_path) * 29


def fodg_total_shape_count_times_twenty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by twenty-nine."""
    return fodg_total_shape_count(file_path) * 29


def fodg_page_count_times_thirty(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty."""
    return fodg_page_count(file_path) * 30


def fodg_total_shape_count_times_thirty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty."""
    return fodg_total_shape_count(file_path) * 30


def fodg_page_count_times_thirty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-one."""
    return fodg_page_count(file_path) * 31


def fodg_total_shape_count_times_thirty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-one."""
    return fodg_total_shape_count(file_path) * 31


def fodg_page_count_times_thirty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-two."""
    return fodg_page_count(file_path) * 32


def fodg_total_shape_count_times_thirty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-two."""
    return fodg_total_shape_count(file_path) * 32


def fodg_page_count_times_thirty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-three."""
    return fodg_page_count(file_path) * 33


def fodg_total_shape_count_times_thirty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-three."""
    return fodg_total_shape_count(file_path) * 33


def fodg_page_count_times_thirty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-four."""
    return fodg_page_count(file_path) * 34


def fodg_total_shape_count_times_thirty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-four."""
    return fodg_total_shape_count(file_path) * 34


def fodg_page_count_times_thirty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-five."""
    return fodg_page_count(file_path) * 35


def fodg_total_shape_count_times_thirty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-five."""
    return fodg_total_shape_count(file_path) * 35


def fodg_page_count_times_thirty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-six."""
    return fodg_page_count(file_path) * 36


def fodg_total_shape_count_times_thirty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-six."""
    return fodg_total_shape_count(file_path) * 36


def fodg_page_count_times_thirty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-seven."""
    return fodg_page_count(file_path) * 37


def fodg_total_shape_count_times_thirty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-seven."""
    return fodg_total_shape_count(file_path) * 37


def fodg_page_count_times_thirty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-eight."""
    return fodg_page_count(file_path) * 38


def fodg_total_shape_count_times_thirty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-eight."""
    return fodg_total_shape_count(file_path) * 38

def fodg_page_count_times_thirty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by thirty-nine."""
    return fodg_page_count(file_path) * 39

def fodg_total_shape_count_times_thirty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by thirty-nine."""
    return fodg_total_shape_count(file_path) * 39

def fodg_page_count_times_forty(file_path: "str | Path") -> int:
    """Return page count multiplied by forty."""
    return fodg_page_count(file_path) * 40

def fodg_total_shape_count_times_forty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty."""
    return fodg_total_shape_count(file_path) * 40


def fodg_text_percentage(file_path: "str | Path") -> float:
    """Return percentage of text items relative to total shapes (0.0 to 100.0). 0.0 if no shapes."""
    ts = fodg_total_shape_count(file_path)
    if ts == 0:
        return 0.0
    return fodg_text_item_count(file_path) / ts * 100.0


def fodg_non_text_shape_percentage(file_path: "str | Path") -> float:
    """Return percentage of non-text shapes relative to total shapes (0.0 to 100.0). 0.0 if no shapes."""
    ts = fodg_total_shape_count(file_path)
    if ts == 0:
        return 0.0
    return fodg_non_text_shape_count(file_path) / ts * 100.0

def fodg_page_count_times_forty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-one."""
    return fodg_page_count(file_path) * 41

def fodg_total_shape_count_times_forty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-one."""
    return fodg_total_shape_count(file_path) * 41

def fodg_page_count_times_forty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-two."""
    return fodg_page_count(file_path) * 42

def fodg_total_shape_count_times_forty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-two."""
    return fodg_total_shape_count(file_path) * 42

def fodg_page_count_times_forty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-three."""
    return fodg_page_count(file_path) * 43

def fodg_total_shape_count_times_forty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-three."""
    return fodg_total_shape_count(file_path) * 43

def fodg_page_count_times_forty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-four."""
    return fodg_page_count(file_path) * 44

def fodg_total_shape_count_times_forty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-four."""
    return fodg_total_shape_count(file_path) * 44

def fodg_page_count_times_forty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-five."""
    return fodg_page_count(file_path) * 45

def fodg_total_shape_count_times_forty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-five."""
    return fodg_total_shape_count(file_path) * 45


def fodg_page_count_times_forty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-six."""
    return fodg_page_count(file_path) * 46


def fodg_total_shape_count_times_forty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-six."""
    return fodg_total_shape_count(file_path) * 46


def fodg_page_count_times_forty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-seven."""
    return fodg_page_count(file_path) * 47


def fodg_total_shape_count_times_forty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-seven."""
    return fodg_total_shape_count(file_path) * 47


def fodg_page_count_times_forty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-eight."""
    return fodg_page_count(file_path) * 48


def fodg_total_shape_count_times_forty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-eight."""
    return fodg_total_shape_count(file_path) * 48


def fodg_page_count_times_forty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by forty-nine."""
    return fodg_page_count(file_path) * 49


def fodg_total_shape_count_times_forty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by forty-nine."""
    return fodg_total_shape_count(file_path) * 49


def fodg_page_count_times_fifty(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty."""
    return fodg_page_count(file_path) * 50


def fodg_total_shape_count_times_fifty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty."""
    return fodg_total_shape_count(file_path) * 50


def fodg_page_count_times_fifty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-one."""
    return fodg_page_count(file_path) * 51


def fodg_total_shape_count_times_fifty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-one."""
    return fodg_total_shape_count(file_path) * 51


def fodg_page_count_times_fifty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-two."""
    return fodg_page_count(file_path) * 52


def fodg_total_shape_count_times_fifty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-two."""
    return fodg_total_shape_count(file_path) * 52


def fodg_page_count_times_fifty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-three."""
    return fodg_page_count(file_path) * 53


def fodg_total_shape_count_times_fifty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-three."""
    return fodg_total_shape_count(file_path) * 53


def fodg_page_count_times_fifty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-four."""
    return fodg_page_count(file_path) * 54


def fodg_total_shape_count_times_fifty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-four."""
    return fodg_total_shape_count(file_path) * 54


def fodg_page_count_times_fifty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-five."""
    return fodg_page_count(file_path) * 55


def fodg_total_shape_count_times_fifty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-five."""
    return fodg_total_shape_count(file_path) * 55


def fodg_page_count_times_fifty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-six."""
    return fodg_page_count(file_path) * 56


def fodg_total_shape_count_times_fifty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-six."""
    return fodg_total_shape_count(file_path) * 56


def fodg_page_count_times_fifty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-seven."""
    return fodg_page_count(file_path) * 57


def fodg_total_shape_count_times_fifty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-seven."""
    return fodg_total_shape_count(file_path) * 57

def fodg_page_count_times_fifty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-eight."""
    return fodg_page_count(file_path) * 58

def fodg_total_shape_count_times_fifty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-eight."""
    return fodg_total_shape_count(file_path) * 58

def fodg_page_count_times_fifty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by fifty-nine."""
    return fodg_page_count(file_path) * 59

def fodg_total_shape_count_times_fifty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by fifty-nine."""
    return fodg_total_shape_count(file_path) * 59

def fodg_page_count_times_sixty(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty."""
    return fodg_page_count(file_path) * 60

def fodg_total_shape_count_times_sixty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty."""
    return fodg_total_shape_count(file_path) * 60

def fodg_page_count_times_sixty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-one."""
    return fodg_page_count(file_path) * 61

def fodg_total_shape_count_times_sixty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-one."""
    return fodg_total_shape_count(file_path) * 61

def fodg_page_count_times_sixty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-two."""
    return fodg_page_count(file_path) * 62

def fodg_total_shape_count_times_sixty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-two."""
    return fodg_total_shape_count(file_path) * 62

def fodg_page_count_times_sixty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-three."""
    return fodg_page_count(file_path) * 63

def fodg_total_shape_count_times_sixty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-three."""
    return fodg_total_shape_count(file_path) * 63

def fodg_page_count_times_sixty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-four."""
    return fodg_page_count(file_path) * 64

def fodg_total_shape_count_times_sixty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-four."""
    return fodg_total_shape_count(file_path) * 64

def fodg_page_count_times_sixty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-five."""
    return fodg_page_count(file_path) * 65

def fodg_total_shape_count_times_sixty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-five."""
    return fodg_total_shape_count(file_path) * 65

def fodg_page_count_times_sixty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-six."""
    return fodg_page_count(file_path) * 66

def fodg_total_shape_count_times_sixty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-six."""
    return fodg_total_shape_count(file_path) * 66

def fodg_page_count_times_sixty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-seven."""
    return fodg_page_count(file_path) * 67

def fodg_total_shape_count_times_sixty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-seven."""
    return fodg_total_shape_count(file_path) * 67

def fodg_page_count_times_sixty_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-eight."""
    return fodg_page_count(file_path) * 68

def fodg_total_shape_count_times_sixty_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-eight."""
    return fodg_total_shape_count(file_path) * 68





def fodg_page_count_times_sixty_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by sixty-nine."""
    return fodg_page_count(file_path) * 69

def fodg_total_shape_count_times_sixty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by sixty-nine."""
    return fodg_total_shape_count(file_path) * 69





def fodg_page_count_times_seventy(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy."""
    return fodg_page_count(file_path) * 70

def fodg_total_shape_count_times_seventy(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy."""
    return fodg_total_shape_count(file_path) * 70

def fodg_page_count_times_seventy_one(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-one."""
    return fodg_page_count(file_path) * 71

def fodg_total_shape_count_times_seventy_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-one."""
    return fodg_total_shape_count(file_path) * 71


def fodg_page_count_times_seventy_two(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-two."""
    return fodg_page_count(file_path) * 72


def fodg_total_shape_count_times_seventy_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-two."""
    return fodg_total_shape_count(file_path) * 72


def fodg_page_count_times_seventy_three(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-three."""
    return fodg_page_count(file_path) * 73


def fodg_total_shape_count_times_seventy_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-three."""
    return fodg_total_shape_count(file_path) * 73


def fodg_page_count_times_seventy_four(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-four."""
    return fodg_page_count(file_path) * 74


def fodg_total_shape_count_times_seventy_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-four."""
    return fodg_total_shape_count(file_path) * 74


def fodg_page_count_times_seventy_five(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-five."""
    return fodg_page_count(file_path) * 75


def fodg_total_shape_count_times_seventy_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-five."""
    return fodg_total_shape_count(file_path) * 75


def fodg_bytes_per_shape(file_path: "str | Path") -> float:
    """Return file size divided by total shape count. 0.0 if no shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return 0.0
    return fodg_file_size_bytes(file_path) / sc


def fodg_text_to_shape_ratio(file_path: "str | Path") -> float:
    """Return text item count divided by total shape count. 0.0 if no shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return 0.0
    return fodg_text_item_count(file_path) / sc


def fodg_page_count_times_seventy_six(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-six."""
    return fodg_page_count(file_path) * 76


def fodg_total_shape_count_times_seventy_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-six."""
    return fodg_total_shape_count(file_path) * 76


def fodg_page_count_times_seventy_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-seven."""
    return fodg_page_count(file_path) * 77


def fodg_total_shape_count_times_seventy_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-seven."""
    return fodg_total_shape_count(file_path) * 77


def fodg_page_count_times_seventy_eight(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-eight."""
    return fodg_page_count(file_path) * 78


def fodg_total_shape_count_times_seventy_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-eight."""
    return fodg_total_shape_count(file_path) * 78





def fodg_page_count_times_seventy_nine(file_path: "str | Path") -> int:
    """Return page count multiplied by seventy-nine."""
    return fodg_page_count(file_path) * 79

def fodg_total_shape_count_times_seventy_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by seventy-nine."""
    return fodg_total_shape_count(file_path) * 79

def fodg_page_count_times_eighty(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty."""
    return fodg_page_count(file_path) * 80

def fodg_total_shape_count_times_eighty(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty."""
    return fodg_total_shape_count(file_path) * 80

def fodg_page_count_times_eighty_one(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-one."""
    return fodg_page_count(file_path) * 81

def fodg_total_shape_count_times_eighty_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-one."""
    return fodg_total_shape_count(file_path) * 81

def fodg_page_count_times_eighty_two(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-two."""
    return fodg_page_count(file_path) * 82

def fodg_total_shape_count_times_eighty_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-two."""
    return fodg_total_shape_count(file_path) * 82

def fodg_page_count_times_eighty_three(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-three."""
    return fodg_page_count(file_path) * 83

def fodg_total_shape_count_times_eighty_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-three."""
    return fodg_total_shape_count(file_path) * 83

def fodg_page_count_times_eighty_four(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-four."""
    return fodg_page_count(file_path) * 84

def fodg_total_shape_count_times_eighty_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-four."""
    return fodg_total_shape_count(file_path) * 84





def fodg_page_count_times_eighty_five(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-five."""
    return fodg_page_count(file_path) * 85

def fodg_total_shape_count_times_eighty_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-five."""
    return fodg_total_shape_count(file_path) * 85





def fodg_page_count_times_eighty_six(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-six."""
    return fodg_page_count(file_path) * 86

def fodg_total_shape_count_times_eighty_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-six."""
    return fodg_total_shape_count(file_path) * 86


def fodg_text_per_page(file_path: "str | Path") -> float:
    """Return text item count divided by page count. 0.0 if no pages."""
    pc = fodg_page_count(file_path)
    if pc == 0:
        return 0.0
    return fodg_text_item_count(file_path) / pc


def fodg_is_text_heavy(file_path: "str | Path") -> bool:
    """Return True if text items exceed half of total shapes."""
    sc = fodg_total_shape_count(file_path)
    if sc == 0:
        return False
    return fodg_text_item_count(file_path) > sc / 2

def fodg_page_count_times_eighty_seven(file_path: "str | Path") -> int:
    """Return page count multiplied by eighty-seven."""
    return fodg_page_count(file_path) * 87

def fodg_total_shape_count_times_eighty_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-seven."""
    return fodg_total_shape_count(file_path) * 87






























def fodg_shape_count_times_eighty_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by eighty-nine."""
    return fodg_total_shape_count(file_path) * 89


def fodg_text_count_times_eighty_nine(file_path: "str | Path") -> int:
    """Return text item count multiplied by eighty-nine."""
    return fodg_text_item_count(file_path) * 89






























def fodg_shape_count_times_ninety(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety."""
    return fodg_total_shape_count(file_path) * 90


def fodg_text_count_times_ninety(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety."""
    return fodg_text_item_count(file_path) * 90










def fodg_shape_count_times_ninety_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-one."""
    return fodg_total_shape_count(file_path) * 91


def fodg_text_count_times_ninety_one(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-one."""
    return fodg_text_item_count(file_path) * 91


def fodg_shape_count_times_ninety_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-two."""
    return fodg_total_shape_count(file_path) * 92


def fodg_text_count_times_ninety_two(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-two."""
    return fodg_text_item_count(file_path) * 92














def fodg_shape_count_times_ninety_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-three."""
    return fodg_total_shape_count(file_path) * 93


def fodg_text_count_times_ninety_three(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-three."""
    return fodg_text_item_count(file_path) * 93










def fodg_shape_count_times_ninety_four(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-four."""
    return fodg_total_shape_count(file_path) * 94


def fodg_text_count_times_ninety_four(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-four."""
    return fodg_text_item_count(file_path) * 94














def fodg_shape_count_times_ninety_five(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-five."""
    return fodg_total_shape_count(file_path) * 95


def fodg_text_count_times_ninety_five(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-five."""
    return fodg_text_item_count(file_path) * 95






def fodg_shape_count_times_ninety_six(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-six."""
    return fodg_total_shape_count(file_path) * 96


def fodg_text_count_times_ninety_six(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-six."""
    return fodg_text_item_count(file_path) * 96














def fodg_shape_count_times_ninety_seven(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-seven."""
    return fodg_total_shape_count(file_path) * 97


def fodg_text_count_times_ninety_seven(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-seven."""
    return fodg_text_item_count(file_path) * 97






def fodg_shape_count_times_ninety_eight(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-eight."""
    return fodg_total_shape_count(file_path) * 98


def fodg_text_count_times_ninety_eight(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-eight."""
    return fodg_text_item_count(file_path) * 98










def fodg_shape_count_times_ninety_nine(file_path: "str | Path") -> int:
    """Return total shape count multiplied by ninety-nine."""
    return fodg_total_shape_count(file_path) * 99


def fodg_text_count_times_ninety_nine(file_path: "str | Path") -> int:
    """Return text item count multiplied by ninety-nine."""
    return fodg_text_item_count(file_path) * 99














def fodg_shape_count_times_one_hundred(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred."""
    return fodg_total_shape_count(file_path) * 100


def fodg_text_count_times_one_hundred(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred."""
    return fodg_text_item_count(file_path) * 100














def fodg_shape_count_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and one."""
    return fodg_total_shape_count(file_path) * 101


def fodg_text_count_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and one."""
    return fodg_text_item_count(file_path) * 101














def fodg_shape_count_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and two."""
    return fodg_total_shape_count(file_path) * 102


def fodg_text_count_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and two."""
    return fodg_text_item_count(file_path) * 102










def fodg_shape_count_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return total shape count multiplied by one hundred and three."""
    return fodg_total_shape_count(file_path) * 103


def fodg_text_count_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return text item count multiplied by one hundred and three."""
    return fodg_text_item_count(file_path) * 103

# ---------------------------------------------------------------------------
# Backward-compat: analytics functions moved to fodg_analytics.py (TC-HEAL-PY-FODG-001)
# Code that imports analytics functions directly from this module still works.
# ---------------------------------------------------------------------------
def __getattr__(name: str):
    """Lazy backward-compat re-export for analytics functions in fodg_analytics.py."""
    if name.startswith("fodg_"):
        try:
            from . import fodg_analytics as _analytics
            val = getattr(_analytics, name, None)
            if val is not None:
                globals()[name] = val  # cache to avoid repeated __getattr__ calls
                return val
        except ImportError:
            pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

