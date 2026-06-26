"""fodg_analytics.py — analytics functions for FODG neutral model dicts.

All functions operate on a model dict produced by fodg_codec.load().
No I/O is performed here — callers must load the model first.
"""

from __future__ import annotations

from typing import Any


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


def get_page_count(model: dict[str, Any]) -> int:
    """Return the number of pages in the document.

    Args:
        model: FODG neutral model dict (must have 'pages' key).

    Returns:
        Integer count of pages. Returns 0 for empty or missing pages list.
    """
    return len(model.get("pages", []))


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
