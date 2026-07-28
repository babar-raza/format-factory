"""fodg_page_ops.py — Extracted FODG page/model manipulation and export functions.

Split out of fodg_codec.py (TC-PA-017 monolith healing) to keep each source module
under the 800-LOC architecture cap. These functions operate on loaded FODG model dicts
(and, for exports, delegate to the core loader); behavior is unchanged from the original
definitions. Core loader/parser helpers, namespace constants, and shape tables that
remain in fodg_codec.py are brought in via the star-import below. Re-exported from
fodg_codec.py so every public name stays importable from its original path.
"""
from __future__ import annotations

from .fodg_codec import *  # noqa: F401,F403 - core loader/constants reused at call time
from .fodg_codec import _read_source  # private helper; not covered by ``import *``


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
