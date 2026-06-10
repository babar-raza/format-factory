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
    create_fodg,
    write_fodg,
    get_shapes,
    get_page_by_name,
    add_page,
    get_text_shapes,
    remove_page,
    rename_page,
    get_all_text,
    count_shapes,
    export_to_json,
    duplicate_page,
    get_page_index,
    clear_page,
    swap_pages,
    page_names,
    has_page,
    probe_fodg,
    export_to_txt,
    export_to_csv,
    roundtrip,
    find_text,
)

__all__ = [
    "FodgError",
    "FodgParseError",
    "load",
    "get_page_count",
    "get_shape_count",
    "extract_text",
    "get_page_metadata",
    "create_fodg",
    "write_fodg",
    "get_shapes",
    "get_page_by_name",
    "add_page",
    "get_text_shapes",
    "remove_page",
    "rename_page",
    "get_all_text",
    "count_shapes",
    "export_to_json",
    "duplicate_page",
    "get_page_index",
    "clear_page",
    "swap_pages",
    "page_names",
    "has_page",
    "probe_fodg",
    "export_to_txt",
    "export_to_csv",
    "roundtrip",
    "find_text",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
