"""
FODP slide analytics — file-path based slide-level statistics.

Extends presentation_document.py with additional analytics.
Uses load, get_page_metadata, and extract_text from fodp_codec.
"""
from __future__ import annotations

from pathlib import Path

from .fodp_codec import load, get_page_metadata, extract_text

spec_qname = "fodp:presentation"
spec_fact_ref = "FACT-FODP-001"


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

    Spec: ODF 1.3 draw:page element (FACT-FODP-001)
    """
    doc = load(source)
    return doc.get("page_count", 0)


def fodp_is_fodp(source: "str | bytes | Path") -> bool:
    """Return True if the document is identified as a flat FODP file.

    Spec: ODF 1.3 MIME type application/vnd.oasis.opendocument.presentation-flat-xml
    (FACT-FODP-001)
    """
    doc = load(source)
    return bool(doc.get("is_fodp", False))


def fodp_first_slide_title(source: "str | bytes | Path") -> str:
    """Return the title text of the first slide. Empty string if no slides.

    Spec: ODF 1.3 draw:page title text (FACT-FODP-001)
    """
    meta = get_page_metadata(source)
    return meta[0].get("title", "") if meta else ""


def fodp_slide_shape_counts(source: "str | bytes | Path") -> list:
    """Return list of shape counts, one entry per slide in presentation order.

    Spec: ODF 1.3 draw:page child shapes (FACT-FODP-001)
    """
    meta = get_page_metadata(source)
    return [s.get("shape_count", 0) for s in meta]


def fodp_total_shape_count(source: "str | bytes | Path") -> int:
    """Return total shape count across all slides.

    Spec: ODF 1.3 draw:page child shapes (FACT-FODP-001)
    """
    meta = get_page_metadata(source)
    return sum(s.get("shape_count", 0) for s in meta)


def fodp_has_text(source: "str | bytes | Path") -> bool:
    """Return True if any slide contains at least one text item.

    Spec: ODF 1.3 text:p child of draw elements (FACT-FODP-001)
    """
    meta = get_page_metadata(source)
    return any(s.get("text_content") for s in meta)
