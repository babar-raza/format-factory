"""
FODG Drawing Document — spec-level domain module.

Implements document-level metrics and predicates for the ODF Drawing format (FODG).
All functions are grounded in ODF 1.3 Part 1 specification elements.

Spec authority : ODF 1.3 Part 1
QName          : office:document
Namespace URI  : urn:oasis:names:tc:opendocument:xmlns:office:1.0
Spec fact ref  : FACT-FODG-EX-0028

This module is a behavioral implementation module, NOT an architecture_only spec stub.
The corresponding spec stub is at src/python/fodg/spec/office/document.py.

Source: Functions migrated from fodg_analytics_extra.py and fodg_analytics.py
        as part of spec-level segregation healing (TC-ANAL-SEG-HEAL-001, 2026-06-22).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .fodg_codec import load, get_shape_count, get_text_shapes

spec_qname = "office:document"
spec_fact_ref = "FACT-FODG-001"
namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

def fodg_total_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of shapes across all pages in a FODG file.

    Args:
        file_path: Path to a FODG file.

    Returns:
        Integer total shape count across all pages.

    Raises:
        FodgError subclasses on parse failure.
    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
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
    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
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
    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
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
    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
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
    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return any(p.get("shape_count", 0) == 0 for p in pages)


def fodg_page_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of pages in the FODG document

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    return len(doc.get("pages", []))


def fodg_all_pages_have_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if every page has at least one shape; False otherwise

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return False
    return all(p.get("shape_count", 0) > 0 for p in pages)


def fodg_text_to_shape_ratio(file_path: "str | bytes | Path") -> float:
    """Return the ratio of text shapes to total shapes. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    total = get_shape_count(file_path)
    if total == 0:
        return 0.0
    doc = load(file_path)
    text_count = len(get_text_shapes(doc))
    return text_count / total


def fodg_max_shapes_per_page(file_path: "str | bytes | Path") -> int:
    """Return the maximum number of shapes on any single page. 0 if no pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return max(p.get("shape_count", 0) for p in pages)


def fodg_min_shapes_per_page(file_path: "str | bytes | Path") -> int:
    """Return the minimum number of shapes on any single page. 0 if no pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return min(p.get("shape_count", 0) for p in pages)


def fodg_shape_density(file_path: "str | bytes | Path") -> float:
    """Return total shapes / page count. 0.0 if no pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = sum(p.get("shape_count", 0) for p in pages)
    return total / len(pages)


def fodg_empty_page_count(file_path: "str | bytes | Path") -> int:
    """Return the number of pages with zero shapes

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages if p.get("shape_count", 0) == 0)


def fodg_is_single_page(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has exactly one page

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    return len(doc.get("pages", [])) == 1


def fodg_total_text_length(file_path: "str | bytes | Path") -> int:
    """Return total character count of all text content in the drawing

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    total = 0
    for page in doc.get("pages", []):
        for shape in page.get("shapes", []):
            total += len(shape.get("text", ""))
    return total


def fodg_has_text(file_path: "str | bytes | Path") -> bool:
    """Return True if any shape in the drawing contains text

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    return fodg_total_text_length(file_path) > 0


def fodg_is_empty_document(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has no shapes on any page

    Spec: ODF 1.3 office:document root element (FACT-FODG-EX-0028)
    """
    return fodg_total_shape_count(file_path) == 0


def fodg_non_text_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the count of shapes that are not text shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    return fodg_total_shape_count(file_path) - fodg_text_shape_count(file_path)


def fodg_avg_text_per_page(file_path: "str | bytes | Path") -> float:
    """Return average character count of text per page. 0.0 if no pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    total = fodg_total_text_length(file_path)
    return total / len(pages)


def fodg_has_multiple_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has more than one page

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    return fodg_page_count(file_path) > 1


def fodg_shape_to_page_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of shape counts across pages. 0.0 if fewer than 2 pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if len(pages) < 2:
        return 0.0
    counts = [p.get("shape_count", 0) for p in pages]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fodg_max_text_per_page(file_path: "str | bytes | Path") -> int:
    """Return the maximum text length on any single page. 0 if no pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    lengths = [sum(len(t) for t in p.get("text_content", [])) for p in pages]
    return max(lengths) if lengths else 0


def fodg_text_per_shape(file_path: "str | bytes | Path") -> float:
    """Return total text length / total shapes. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    shapes = fodg_total_shape_count(file_path)
    if shapes == 0:
        return 0.0
    return fodg_total_text_length(file_path) / shapes


def fodg_nonempty_page_count(file_path: "str | bytes | Path") -> int:
    """Return the count of pages that have at least one shape

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages if p.get("shape_count", 0) > 0)


def fodg_text_density(file_path: "str | bytes | Path") -> float:
    """Return total text length / total shape count. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    total_shapes = fodg_total_shape_count(file_path)
    if total_shapes == 0:
        return 0.0
    return fodg_total_text_length(file_path) / total_shapes


def fodg_is_multi_page(file_path: "str | bytes | Path") -> bool:
    """Return True if document has more than one page

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    return fodg_page_count(file_path) > 1


def fodg_shape_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of shape counts across pages. 0.0 if fewer than 2 pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if len(pages) < 2:
        return 0.0
    counts = [len(p.get("shapes", [])) for p in pages]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fodg_is_text_only(file_path: "str | bytes | Path") -> bool:
    """Return True if all shapes are text shapes (text_shape_count == total_shape_count)

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    total = fodg_total_shape_count(file_path)
    if total == 0:
        return False
    return fodg_text_shape_count(file_path) == total


def fodg_avg_shapes_per_nonempty_page(file_path: "str | bytes | Path") -> float:
    """Return average shape count per non-empty page. 0.0 if no non-empty pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    nonempty = [p.get("shape_count", 0) for p in pages if p.get("shape_count", 0) > 0]
    if not nonempty:
        return 0.0
    return sum(nonempty) / len(nonempty)


def fodg_has_single_shape(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains exactly one shape across all pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    return fodg_total_shape_count(file_path) == 1


def fodg_page_text_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of text lengths across pages. 0.0 if fewer than 2 pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
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
    """Return total character count of all text in all shapes across all pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    total = 0
    for p in doc.get("pages", []):
        for s in p.get("shapes", []):
            total += len(s.get("text", ""))
    return total


def fodg_avg_text_per_shape(file_path: "str | bytes | Path") -> float:
    """Return average text length per shape. 0.0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    lengths = []
    for p in doc.get("pages", []):
        for s in p.get("shapes", []):
            lengths.append(len(s.get("text", "")))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def fodg_min_text_per_page(file_path: "str | bytes | Path") -> int:
    """Return the minimum total text length of any page. 0 if no pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
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
    """Return total count of text content items across all pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(len(pg.get("text_content", [])) for pg in pages)


def fodg_nonempty_shape_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of shapes with non-empty text to total shapes. 0.0 if no shapes

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    all_shapes = [s for p in doc.get("pages", []) for s in p.get("shapes", [])]
    if not all_shapes:
        return 0.0
    nonempty = sum(1 for s in all_shapes if s.get("text", "").strip())
    return nonempty / len(all_shapes)


def fodg_max_shape_text_length(file_path: "str | bytes | Path") -> int:
    """Return length of text in the shape with the most text. 0 if no shapes

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    lengths = [
        len(s.get("text", ""))
        for p in doc.get("pages", [])
        for s in p.get("shapes", [])
    ]
    return max(lengths) if lengths else 0


def fodg_shapes_with_text_count(file_path: "str | bytes | Path") -> int:
    """Return count of shapes that have non-empty text content

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    return sum(
        1 for p in doc.get("pages", [])
        for s in p.get("shapes", [])
        if s.get("text", "").strip()
    )


def fodg_nonempty_page_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of pages with at least one shape to total pages. 0.0 if no pages

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    nonempty = sum(1 for p in pages if p.get("shapes") or p.get("shape_count", 0) > 0)
    return nonempty / len(pages)


def fodg_total_shapes_and_pages(file_path: "str | bytes | Path") -> int:
    """Return combined count of total shapes plus total pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    total_shapes = sum(p.get("shape_count", 0) for p in pages)
    return total_shapes + len(pages)


def fodg_has_non_text_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if any page contains at least one non-text shape

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    return fodg_non_text_shape_count(file_path) > 0


def fodg_has_no_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains no shapes on any page

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(p.get("shape_count", 0) for p in pages) == 0


def fodg_all_pages_have_text(file_path: "str | bytes | Path") -> bool:
    """Return True if every page has at least one non-empty text content item.

    Args:
        file_path: Path to the .fodg file.

    Returns:
        True if all pages have non-empty text; False if any page has no text or doc is empty.
    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
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
    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return max(lengths) if lengths else 0


def fodg_file_size_bytes(file_path: "str | bytes | Path") -> int:
    """Return the file size in bytes

    Spec: ODF 1.3 office:document root element (FACT-FODG-EX-0028)
    """
    from pathlib import Path as _Path
    return _Path(file_path).stat().st_size


def fodg_min_text_item_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the shortest non-empty text item across all pages. 0 if none

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return min(lengths) if lengths else 0


def fodg_avg_text_item_length(file_path: "str | bytes | Path") -> float:
    """Return average length of text items across all pages. 0.0 if none

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    lengths = [len(t) for p in pages for t in p.get("text_content", []) if t.strip()]
    return sum(lengths) / len(lengths) if lengths else 0.0


def fodg_unique_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return count of distinct non-empty text items across all pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    texts = {t.strip() for p in pages for t in p.get("text_content", []) if t.strip()}
    return len(texts)


def fodg_text_item_count(file_path: "str | bytes | Path") -> int:
    """Return total count of non-empty text items across all pages

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return sum(1 for p in pages for t in p.get("text_content", []) if t.strip())


def fodg_has_text_content(file_path: "str | bytes | Path") -> bool:
    """Return True if any page has non-empty text content

    Spec: ODF 1.3 draw:text-box child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    for p in doc.get("pages", []):
        for t in p.get("text_content", []):
            if t.strip():
                return True
    return False


def fodg_max_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum shape count on any single page. 0 if no pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return max(p.get("shape_count", 0) for p in pages)


def fodg_min_shape_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum shape count on any single page. 0 if no pages

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0
    return min(p.get("shape_count", 0) for p in pages)


def fodg_is_empty_drawing(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing has no shapes on any page

    Spec: ODF 1.3 office:document root element (FACT-FODG-EX-0028)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    return all(p.get("shape_count", 0) == 0 for p in pages)


def fodg_has_multiple_shapes(file_path: "str | bytes | Path") -> bool:
    """Return True if the drawing contains more than one shape in total

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    return fodg_total_shape_count(file_path) > 1


def fodg_has_single_page(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains exactly one page.

    Spec: ODF 1.3 draw:page child of office:drawing (FACT-FODG-001)
    """
    doc = load(file_path)
    return doc.get("page_count", 0) == 1


def fodg_page_names(file_path: "str | bytes | Path") -> list:
    """Return list of page names in document order.

    Spec: ODF 1.3 draw:page@draw:name attribute (FACT-FODG-001)
    """
    doc = load(file_path)
    return [p.get("name", "") for p in doc.get("pages", [])]


def fodg_average_shape_count(file_path: "str | bytes | Path") -> float:
    """Return average number of shapes per page. 0.0 if no pages.

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return 0.0
    return doc.get("shapes_total", 0) / len(pages)


def fodg_pages_with_shapes_count(file_path: "str | bytes | Path") -> int:
    """Return count of pages that contain at least one shape.

    Spec: ODF 1.3 draw:custom-shape child of draw:page (FACT-FODG-002)
    """
    doc = load(file_path)
    return sum(1 for p in doc.get("pages", []) if p.get("shape_count", 0) > 0)


def fodg_total_text_length(file_path: "str | bytes | Path") -> int:
    """Return total character count across all text items on all pages.

    Spec: ODF 1.3 text:p child of draw elements (FACT-FODG-003)
    """
    doc = load(file_path)
    total = 0
    for page in doc.get("pages", []):
        for text in page.get("text_content", []):
            total += len(text)
    return total


def fodg_has_text_on_all_pages(file_path: "str | bytes | Path") -> bool:
    """Return True if every page has at least one text item.

    Spec: ODF 1.3 text:p child of draw elements (FACT-FODG-003)
    """
    doc = load(file_path)
    pages = doc.get("pages", [])
    if not pages:
        return False
    return all(len(p.get("text_content", [])) > 0 for p in pages)


try:
    from .drawing_metrics import *  # noqa: F401, F403
except ImportError:
    pass
