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
