"""
format-factory: FODP (Flat OpenDocument Presentation) FOSS Python track.

Minimal FOSS implementation for .fodp format support.
ODF 1.3 Part 3 specification — OASIS Royalty-Free Category 1.
Acquisition Gates 1-3 PASSED. Gates 4-7 delegated PASS (R20).

FOSS track only — no commercial readiness implied.
See: acquisition-packs/fodp/ for gate evidence.
"""

from .fodp_codec import (
    FodpError,
    FodpParseError,
    load,
    get_page_count,
    extract_text,
    get_page_metadata,
    fodp_total_text_length,
    fodp_slide_count,
    fodp_slide_shape_counts,
    fodp_total_shape_count,
    fodp_notes_text,
    fodp_has_notes,
    fodp_slide_titles,
    fodp_image_count,
    fodp_empty_slide_count,
)

__all__ = [
    "FodpError",
    "FodpParseError",
    "load",
    "get_page_count",
    "extract_text",
    "get_page_metadata",
    "fodp_total_text_length",
    "fodp_slide_count",
    "fodp_slide_shape_counts",
    "fodp_total_shape_count",
    "fodp_notes_text",
    "fodp_has_notes",
    "fodp_slide_titles",
    "fodp_image_count",
    "fodp_empty_slide_count",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
