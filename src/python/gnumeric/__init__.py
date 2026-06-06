"""
format-factory: Gnumeric FOSS Python track.

Minimal FOSS implementation for .gnumeric format support.
Gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""

from .gnumeric_codec import (
    GnumericError,
    GnumericParseError,
    load,
    get_sheet_count,
    get_cell_count,
    extract_values,
    get_sheet_metadata,
    export_to_csv,
    export_to_json,
    probe_gnumeric,
    create_gnumeric,
    write_gnumeric,
)

__all__ = [
    "GnumericError",
    "GnumericParseError",
    "load",
    "get_sheet_count",
    "get_cell_count",
    "extract_values",
    "get_sheet_metadata",
    "export_to_csv",
    "export_to_json",
    "probe_gnumeric",
    "create_gnumeric",
    "write_gnumeric",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
