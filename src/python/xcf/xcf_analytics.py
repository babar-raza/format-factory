"""
XCF analytics functions.

Arithmetic combination and derivative functions extracted from xcf_parser.py to keep
the core parser file within its baseline_loc_cap of 3997 lines.

Core domain functions remain in xcf_parser. These functions are re-exported via
xcf_parser's 'from .xcf_analytics import *' for backward compatibility.

Do NOT add new functions to this file without a corresponding GAP-ledger entry.
"""
from __future__ import annotations

import os
from pathlib import Path

from .xcf_parser import (
    parse_xcf_strict,
    xcf_file_size_bytes,
    xcf_file_size_per_pixel,
    xcf_height,
    xcf_height_squared,
    xcf_image_type_id,
    xcf_is_landscape,
    xcf_layer_count,
    xcf_total_pixel_count,
    xcf_width,
    xcf_width_squared,
)


def xcf_is_landscape(file_path: "str | Path") -> bool:
    """Return True if width is strictly greater than height."""
    img = parse_xcf_strict(file_path)
    return img.width > img.height
