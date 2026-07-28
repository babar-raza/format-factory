"""
FODP slide analytics — file-path based slide-level statistics.

Extends presentation_document.py with additional analytics.
Uses load, get_page_metadata, and extract_text from fodp_codec.
"""
from __future__ import annotations

from pathlib import Path

from .fodp_codec import load, get_page_metadata, extract_text

spec_qname = "fodp:presentation"
spec_fact_ref = "SAL-FODP-00001"


def fodp_slide_name_list(source: "str | bytes | Path") -> list:
    """Return list of slide internal names (not titles) in slide order.

    These are the draw:page@draw:name values, distinct from slide title text.
    """
    meta = get_page_metadata(source)
    return [s.get("name", "") for s in meta]


def fodp_total_text_items(source: "str | bytes | Path") -> int:
    """Return total count of text items across all slides."""
    meta = get_page_metadata(source)
    return sum(len(s.get("text_content", [])) for s in meta)


def fodp_slides_with_text_count(source: "str | bytes | Path") -> int:
    """Return count of slides that have at least one text item."""
    meta = get_page_metadata(source)
    return sum(1 for s in meta if s.get("text_content"))


def fodp_max_slide_text_items(source: "str | bytes | Path") -> int:
    """Return maximum number of text items on any single slide. 0 if no slides."""
    meta = get_page_metadata(source)
    if not meta:
        return 0
    return max(len(s.get("text_content", [])) for s in meta)


def fodp_min_slide_text_items(source: "str | bytes | Path") -> int:
    """Return minimum number of text items on any single slide. 0 if no slides."""
    meta = get_page_metadata(source)
    if not meta:
        return 0
    return min(len(s.get("text_content", [])) for s in meta)


def fodp_all_slides_have_titles(source: "str | bytes | Path") -> bool:
    """Return True if every slide has a non-empty title string.

    True vacuously when there are no slides.
    """
    meta = get_page_metadata(source)
    if not meta:
        return True
    return all(bool(s.get("title", "").strip()) for s in meta)


def fodp_slide_count(source: "str | bytes | Path") -> int:
    """Return the total number of slides in the FODP presentation.

    Spec: ODF 1.3 draw:page element (SAL-FODP-00001)
    """
    doc = load(source)
    return doc.get("page_count", 0)


def fodp_is_fodp(source: "str | bytes | Path") -> bool:
    """Return True if the document is identified as a flat FODP file.

    Spec: ODF 1.3 MIME type application/vnd.oasis.opendocument.presentation-flat-xml
    (SAL-FODP-00001)
    """
    doc = load(source)
    return bool(doc.get("is_fodp", False))


def fodp_first_slide_title(source: "str | bytes | Path") -> str:
    """Return the title text of the first slide. Empty string if no slides.

    Spec: ODF 1.3 draw:page title text (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return meta[0].get("title", "") if meta else ""


def fodp_slide_shape_counts(source: "str | bytes | Path") -> list:
    """Return list of shape counts, one entry per slide in presentation order.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return [s.get("shape_count", 0) for s in meta]


def fodp_total_shape_count(source: "str | bytes | Path") -> int:
    """Return total shape count across all slides.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return sum(s.get("shape_count", 0) for s in meta)


def fodp_has_text(source: "str | bytes | Path") -> bool:
    """Return True if any slide contains at least one text item.

    Spec: ODF 1.3 text:p child of draw elements (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return any(s.get("text_content") for s in meta)


def fodp_slide_titles(source: "str | bytes | Path") -> list:
    """Return list of all slide title strings in presentation order.

    Spec: ODF 1.3 draw:page title text (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return [s.get("title", "") for s in meta]


def fodp_has_multiple_slides(source: "str | bytes | Path") -> bool:
    """Return True if the presentation contains more than one slide.

    Spec: ODF 1.3 draw:page element (SAL-FODP-00001)
    """
    doc = load(source)
    return doc.get("page_count", 0) > 1


def fodp_avg_shapes_per_slide(source: "str | bytes | Path") -> float:
    """Return average number of shapes per slide. 0.0 if no slides.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    if not meta:
        return 0.0
    return sum(s.get("shape_count", 0) for s in meta) / len(meta)


def fodp_slides_with_shapes_count(source: "str | bytes | Path") -> int:
    """Return count of slides that contain at least one shape.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return sum(1 for s in meta if s.get("shape_count", 0) > 0)


def fodp_all_text_items(source: "str | bytes | Path") -> list:
    """Return flat list of all text items across all slides in order.

    Spec: ODF 1.3 text:p child of draw elements (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    result = []
    for s in meta:
        result.extend(s.get("text_content", []))
    return result


def fodp_slide_names_are_unique(source: "str | bytes | Path") -> bool:
    """Return True if all slide internal names are distinct.

    Spec: ODF 1.3 draw:page@draw:name (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    names = [s.get("name", "") for s in meta]
    return len(names) == len(set(names))


def fodp_last_slide_title(source: "str | bytes | Path") -> str:
    """Return the title text of the last slide. Empty string if no slides.

    Spec: ODF 1.3 draw:page title text (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return meta[-1].get("title", "") if meta else ""


def fodp_slide_text_counts(source: "str | bytes | Path") -> list:
    """Return list of text item counts per slide in presentation order.

    Spec: ODF 1.3 text:p child of draw elements (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return [len(s.get("text_content", [])) for s in meta]


def fodp_max_shape_count(source: "str | bytes | Path") -> int:
    """Return the maximum shape count on any single slide. 0 if no slides.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    if not meta:
        return 0
    return max(s.get("shape_count", 0) for s in meta)


def fodp_min_shape_count(source: "str | bytes | Path") -> int:
    """Return the minimum shape count on any single slide. 0 if no slides.

    Spec: ODF 1.3 draw:page child shapes (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    if not meta:
        return 0
    return min(s.get("shape_count", 0) for s in meta)


def fodp_all_text_items_flat(source: "str | bytes | Path") -> list:
    """Return deduplicated list of all unique text items across all slides.

    Spec: ODF 1.3 text:p child of draw elements (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    seen: dict = {}
    for s in meta:
        for t in s.get("text_content", []):
            seen[t] = None
    return list(seen.keys())


def fodp_slides_without_text_count(source: "str | bytes | Path") -> int:
    """Return count of slides that have no text content.

    Spec: ODF 1.3 text:p child of draw elements (SAL-FODP-00001)
    """
    meta = get_page_metadata(source)
    return sum(1 for s in meta if not s.get("text_content"))
