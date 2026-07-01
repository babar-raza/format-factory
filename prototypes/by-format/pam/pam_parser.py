"""
PAM Gate 4 Prototype Parser — Gate 4 acquisition prototype.

Portable Arbitrary Map (.pam) — P7 netpbm format.
This is a PROTOTYPE only. Not for production use.

Acquisition gates: G1 passed, G2 passed_fast_path, G3 passed.
Gate 4 prototype: this file.

Scope: parse P7 header fields (WIDTH, HEIGHT, DEPTH, MAXVAL, TUPLTYPE)
and validate the raster data length.
Security: bounded input limits enforced.
No neutral model, no writer, no production API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ---- Constants (Gate 4 scope bounds) ----
MAX_FILE_BYTES = 50 * 1024 * 1024   # 50 MB hard limit
MAX_WIDTH = 4096
MAX_HEIGHT = 4096
MAX_DEPTH = 4
MAX_MAXVAL = 65535

PAM_MAGIC = b"P7"
REQUIRED_HEADER_FIELDS = {"WIDTH", "HEIGHT", "DEPTH", "MAXVAL"}
OPTIONAL_HEADER_FIELDS = {"TUPLTYPE"}


class PamParseError(Exception):
    """Raised when PAM parsing fails at the prototype level."""


def is_pam(source: str | bytes | Path) -> bool:
    """Return True if source begins with the P7 magic token."""
    if isinstance(source, Path):
        try:
            header = source.read_bytes()[:4]
        except OSError:
            return False
    elif isinstance(source, str):
        header = source[:4].encode("utf-8", errors="replace")
    else:
        header = source[:4]
    return header[:2] == PAM_MAGIC and (len(header) < 3 or header[2:3] in (b"\n", b"\r", b" "))


def parse_pam(source: str | bytes | Path) -> dict[str, Any]:
    """Parse a PAM (P7) file and return structured data.

    Args:
        source: File path (str or Path) or raw content (bytes).

    Returns:
        Dict with:
          format_id: 'pam'
          width: int
          height: int
          depth: int
          maxval: int
          tupltype: str | None
          bytes_per_sample: int  (1 if maxval<=255, 2 otherwise)
          raster_size: int       (width * height * depth * bytes_per_sample)
          raster_length_valid: bool
          error: None on success

    Raises:
        PamParseError: on invalid magic, missing required fields, or raster mismatch.
    """
    # Load content
    if isinstance(source, Path):
        size = source.stat().st_size
        if size > MAX_FILE_BYTES:
            raise PamParseError(f"File exceeds {MAX_FILE_BYTES} byte limit")
        data = source.read_bytes()
    elif isinstance(source, str):
        data = source.encode("utf-8", errors="replace")
    else:
        data = bytes(source)

    if len(data) > MAX_FILE_BYTES:
        raise PamParseError(f"Input exceeds {MAX_FILE_BYTES} byte limit")

    # --- 1. Validate magic ---
    if not data[:2] == PAM_MAGIC:
        raise PamParseError(
            f"Invalid PAM magic: expected b'P7', got {data[:2]!r}"
        )
    if len(data) < 3 or data[2:3] not in (b"\n", b"\r", b" "):
        raise PamParseError("P7 magic not followed by whitespace/newline")

    # --- 2. Parse header lines until ENDHDR ---
    header_fields: dict[str, str] = {}
    endhdr_pos: int | None = None
    pos = 3  # skip "P7\n"

    # Read lines from the byte stream
    lines_raw = data.split(b"\n")
    byte_offset = 0
    header_line_count = 0

    for line_bytes in lines_raw:
        line = line_bytes.decode("ascii", errors="replace").strip()
        byte_offset += len(line_bytes) + 1  # +1 for the \n

        if not line or line.startswith("#"):
            header_line_count += 1
            continue  # skip blank lines and comments

        if line == "ENDHDR":
            endhdr_pos = byte_offset
            break

        parts = line.split(None, 1)
        if len(parts) == 2:
            field_name, field_value = parts[0], parts[1]
        elif len(parts) == 1:
            field_name, field_value = parts[0], ""
        else:
            continue

        if field_name in REQUIRED_HEADER_FIELDS | OPTIONAL_HEADER_FIELDS:
            header_fields[field_name] = field_value

        header_line_count += 1
        if header_line_count > 100:
            raise PamParseError("Header exceeds 100 lines — possible malformed PAM")

    if endhdr_pos is None:
        raise PamParseError("PAM header missing ENDHDR token")

    # --- 3. Validate required fields ---
    missing = REQUIRED_HEADER_FIELDS - set(header_fields)
    if missing:
        raise PamParseError(f"PAM header missing required fields: {missing}")

    try:
        width = int(header_fields["WIDTH"])
        height = int(header_fields["HEIGHT"])
        depth = int(header_fields["DEPTH"])
        maxval = int(header_fields["MAXVAL"])
    except ValueError as exc:
        raise PamParseError(f"Non-integer value in PAM header fields") from exc

    tupltype = header_fields.get("TUPLTYPE")

    # Security bounds
    if width <= 0 or width > MAX_WIDTH:
        raise PamParseError(f"Width {width} out of bounds (1–{MAX_WIDTH})")
    if height <= 0 or height > MAX_HEIGHT:
        raise PamParseError(f"Height {height} out of bounds (1–{MAX_HEIGHT})")
    if depth <= 0 or depth > MAX_DEPTH:
        raise PamParseError(f"Depth {depth} out of bounds (1–{MAX_DEPTH})")
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PamParseError(f"Maxval {maxval} out of bounds (1–{MAX_MAXVAL})")

    # --- 4. Validate raster length ---
    bytes_per_sample = 1 if maxval <= 255 else 2
    raster_size = width * height * depth * bytes_per_sample
    raster_data = data[endhdr_pos:]
    raster_length_valid = len(raster_data) == raster_size

    return {
        "format_id": "pam",
        "width": width,
        "height": height,
        "depth": depth,
        "maxval": maxval,
        "tupltype": tupltype,
        "bytes_per_sample": bytes_per_sample,
        "raster_size": raster_size,
        "raster_actual_bytes": len(raster_data),
        "raster_length_valid": raster_length_valid,
        "error": None,
    }


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pam_parser.py <file.pam>")
        sys.exit(1)
    try:
        result = parse_pam(Path(sys.argv[1]))
        print(json.dumps(result, indent=2))
    except PamParseError as e:
        print(f"PamParseError: {e}", file=sys.stderr)
        sys.exit(1)
