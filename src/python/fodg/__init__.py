"""
format-factory: FODG (Flat OpenDocument Graphics) FOSS Python track.

Minimal FOSS implementation for .fodg format support.
ODF 1.3 Part 3 specification — OASIS Royalty-Free Category 1.
Acquisition Gates 1-3 PASSED. Gates 4-7 delegated PASS (R20).

FOSS track only — no commercial readiness implied.
"""

from .fodg_codec import (
    FodgError,
    FodgParseError,
    load,
    get_page_count,
    get_shape_count,
    extract_text,
    get_page_metadata,
)

__all__ = [
    "FodgError",
    "FodgParseError",
    "load",
    "get_page_count",
    "get_shape_count",
    "extract_text",
    "get_page_metadata",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
