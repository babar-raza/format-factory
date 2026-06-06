"""
format-factory: ABW (AbiWord) FOSS Python track.

Minimal FOSS implementation for .abw format support.
AWML 1.0 plain XML format.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""

from .abw_codec import (
    AbwError,
    AbwParseError,
    load,
    get_section_count,
    get_paragraph_count,
    extract_text,
    create_abw,
    write_abw,
    probe_abw,
    export_to_txt,
    export_to_html,
    get_metadata,
)

__all__ = [
    "AbwError",
    "AbwParseError",
    "load",
    "get_section_count",
    "get_paragraph_count",
    "extract_text",
    "create_abw",
    "write_abw",
    "probe_abw",
    "export_to_txt",
    "export_to_html",
    "get_metadata",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
