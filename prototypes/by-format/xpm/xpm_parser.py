"""
XPM Gate 4 Prototype Parser — Gate 4 acquisition prototype.

X PixMap (.xpm) — XPM3 format.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed, G3 passed.
Gate 4 prototype: this file.

Scope: parse XPM3 signature, dimensions, color table, and pixel rows.
Security: bounded input limits enforced.
No neutral model, no writer, no production API.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# ---- Constants (Gate 4 scope bounds) ----
MAX_FILE_BYTES = 10 * 1024 * 1024   # 10 MB hard limit
MAX_WIDTH = 4096
MAX_HEIGHT = 4096
MAX_COLORS = 256
MAX_CHARS_PER_PIXEL = 16

XPM3_MAGIC = "/* XPM */"


class XpmParseError(Exception):
    """Raised when XPM3 parsing fails at the prototype level."""


def is_xpm3(source: str | bytes | Path) -> bool:
    """Return True if source begins with the XPM3 magic line '/* XPM */'."""
    if isinstance(source, Path):
        try:
            header = source.read_text(encoding="utf-8", errors="replace")[:20]
        except OSError:
            return False
    elif isinstance(source, bytes):
        header = source[:20].decode("utf-8", errors="replace")
    else:
        header = source[:20]
    return header.strip().startswith(XPM3_MAGIC)


def parse_xpm3(source: str | bytes | Path) -> dict[str, Any]:
    """Parse an XPM3 file and return structured data.

    Args:
        source: File path (str or Path) or raw content (str or bytes).

    Returns:
        Dict with:
          format_id: 'xpm'
          width: int
          height: int
          ncolors: int
          chars_per_pixel: int
          colors: list[dict] — each with symbol, color_type, color_value
          pixel_rows: list[str] — raw pixel row strings
          error: None on success

    Raises:
        XpmParseError: on invalid magic, malformed dimensions, or truncated data.
    """
    # Load content
    if isinstance(source, Path):
        if source.stat().st_size > MAX_FILE_BYTES:
            raise XpmParseError(f"File exceeds {MAX_FILE_BYTES} byte limit")
        content = source.read_text(encoding="utf-8", errors="replace")
    elif isinstance(source, bytes):
        if len(source) > MAX_FILE_BYTES:
            raise XpmParseError(f"Input exceeds {MAX_FILE_BYTES} byte limit")
        content = source.decode("utf-8", errors="replace")
    else:
        content = source

    # --- 1. Validate magic ---
    first_line = content.strip().split("\n")[0].strip()
    if first_line != XPM3_MAGIC:
        raise XpmParseError(
            f"Invalid XPM3 magic: expected '/* XPM */', got {first_line!r}"
        )

    # --- 2. Extract all quoted strings (the XPM data values) ---
    # XPM stores data as C string literals inside a char* array.
    # We extract all "..." quoted tokens between the outer braces.
    brace_start = content.find("{")
    brace_end = content.rfind("}")
    if brace_start == -1 or brace_end == -1 or brace_end <= brace_start:
        raise XpmParseError("XPM3 data block not found (missing { })")

    body = content[brace_start + 1:brace_end]
    # Find all quoted strings (handling escaped quotes is out of Gate 4 scope)
    quoted = re.findall(r'"([^"]*)"', body)
    if not quoted:
        raise XpmParseError("No quoted data strings found in XPM3 body")

    # --- 3. Parse dimensions string: "W H N C" ---
    dims_str = quoted[0]
    parts = dims_str.split()
    if len(parts) < 4:
        raise XpmParseError(
            f"Malformed XPM3 dimensions string: {dims_str!r} "
            "(expected 'width height ncolors chars_per_pixel')"
        )
    try:
        width = int(parts[0])
        height = int(parts[1])
        ncolors = int(parts[2])
        chars_per_pixel = int(parts[3])
    except ValueError as exc:
        raise XpmParseError(
            f"Non-integer value in XPM3 dimensions: {dims_str!r}"
        ) from exc

    # Security bounds
    if width <= 0 or width > MAX_WIDTH:
        raise XpmParseError(f"Width {width} out of bounds (1–{MAX_WIDTH})")
    if height <= 0 or height > MAX_HEIGHT:
        raise XpmParseError(f"Height {height} out of bounds (1–{MAX_HEIGHT})")
    if ncolors <= 0 or ncolors > MAX_COLORS:
        raise XpmParseError(f"Color count {ncolors} out of bounds (1–{MAX_COLORS})")
    if chars_per_pixel <= 0 or chars_per_pixel > MAX_CHARS_PER_PIXEL:
        raise XpmParseError(
            f"chars_per_pixel {chars_per_pixel} out of bounds (1–{MAX_CHARS_PER_PIXEL})"
        )

    # --- 4. Parse color table (ncolors entries) ---
    expected_total = 1 + ncolors + height
    if len(quoted) < expected_total:
        raise XpmParseError(
            f"Truncated XPM3: expected {expected_total} data strings "
            f"(1 dims + {ncolors} colors + {height} pixel rows), "
            f"got {len(quoted)}"
        )

    colors: list[dict[str, str]] = []
    for i in range(1, 1 + ncolors):
        entry = quoted[i]
        # Format: "<symbol> <color_type> <color_value> ..."
        # symbol is chars_per_pixel characters, then key-value pairs
        if len(entry) < chars_per_pixel + 3:
            raise XpmParseError(f"Malformed color entry: {entry!r}")
        symbol = entry[:chars_per_pixel]
        rest = entry[chars_per_pixel:].split()
        if len(rest) < 2:
            raise XpmParseError(f"Color entry missing key/value: {entry!r}")
        colors.append({
            "symbol": symbol,
            "color_type": rest[0],
            "color_value": rest[1],
        })

    # --- 5. Parse pixel rows ---
    pixel_rows: list[str] = []
    for i in range(1 + ncolors, 1 + ncolors + height):
        row = quoted[i]
        expected_row_len = width * chars_per_pixel
        if len(row) != expected_row_len:
            raise XpmParseError(
                f"Pixel row {i - ncolors} length {len(row)} "
                f"does not match expected {expected_row_len} "
                f"(width={width}, chars_per_pixel={chars_per_pixel})"
            )
        pixel_rows.append(row)

    return {
        "format_id": "xpm",
        "width": width,
        "height": height,
        "ncolors": ncolors,
        "chars_per_pixel": chars_per_pixel,
        "colors": colors,
        "pixel_rows": pixel_rows,
        "error": None,
    }


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python xpm_parser.py <file.xpm>")
        sys.exit(1)
    try:
        result = parse_xpm3(Path(sys.argv[1]))
        print(json.dumps(result, indent=2))
    except XpmParseError as e:
        print(f"XpmParseError: {e}", file=sys.stderr)
        sys.exit(1)
