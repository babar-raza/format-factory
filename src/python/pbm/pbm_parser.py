"""
pbm_parser.py — PBM (Portable Bitmap) parser for format-factory-pbm.

Public API:
  parse_pbm(file_path)        — returns result dict (never raises)
  parse_pbm_strict(file_path) — raises PbmError on failure
  probe_pbm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P1 (ASCII) and P4 (binary) PBM files.
Technology: Python stdlib only (open/read/split).

R55 Train F: P4 binary decode added (TC-BINARY-PBM-001).

License: Apache-2.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 65536


class PbmError(Exception):
    """Base exception for PBM parser errors."""


class PbmInvalidMagicError(PbmError):
    """Raised when file does not start with P1 or P4."""


class PbmInvalidHeaderError(PbmError):
    """Raised when header fields are invalid."""


class PbmSizeError(PbmError):
    """Raised when file or image dimensions exceed limits."""


class PbmDecodeError(PbmError):
    """Raised when pixel data is malformed."""


@dataclass
class PbmImage:
    width: int = 0
    height: int = 0
    magic: str = "P1"
    pixels: list[int] = field(default_factory=list)
    path: str = ""


def _strip_comments(text: str) -> str:
    """Remove # comments from PBM text."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        idx = line.find("#")
        if idx >= 0:
            line = line[:idx]
        cleaned.append(line)
    return "\n".join(cleaned)


def _parse_netpbm_header_bytes(data: bytes, num_ints: int) -> tuple[list[int], int]:
    """Parse ASCII Netpbm header from raw bytes, returning (values, data_offset)."""
    i = 0
    n = len(data)

    def skip_ws_and_comments() -> None:
        nonlocal i
        while i < n:
            b = data[i:i+1]
            if b in (b' ', b'\t', b'\n', b'\r'):
                i += 1
            elif b == b'#':
                while i < n and data[i:i+1] != b'\n':
                    i += 1
            else:
                break

    skip_ws_and_comments()
    while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
        i += 1

    values: list[int] = []
    for _ in range(num_ints):
        skip_ws_and_comments()
        start = i
        while i < n and data[i:i+1] not in (b' ', b'\t', b'\n', b'\r'):
            i += 1
        if start == i:
            raise ValueError("Unexpected end of header")
        values.append(int(data[start:i]))

    if i < n:
        i += 1  # consume single whitespace delimiter before binary data

    return values, i


def _parse_p4_binary(path: Path, data: bytes) -> "PbmImage":
    """Decode a P4 (binary packed-bits) PBM file."""
    try:
        (width, height), data_offset = _parse_netpbm_header_bytes(data, 2)
    except (ValueError, IndexError) as exc:
        raise PbmInvalidHeaderError(f"Invalid P4 header: {exc}")

    if width <= 0 or height <= 0:
        raise PbmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}")

    row_bytes = (width + 7) // 8
    expected_bytes = row_bytes * height
    pixel_data = data[data_offset:]

    if len(pixel_data) < expected_bytes:
        raise PbmDecodeError(
            f"Not enough binary pixel data: expected {expected_bytes} bytes, "
            f"got {len(pixel_data)}"
        )

    pixels: list[int] = []
    for row in range(height):
        row_start = row * row_bytes
        for col in range(width):
            byte_idx = row_start + col // 8
            bit_idx = 7 - (col % 8)
            v = (pixel_data[byte_idx] >> bit_idx) & 1
            pixels.append(v)

    return PbmImage(width=width, height=height, magic="P4", pixels=pixels, path=str(path))


def parse_pbm_strict(file_path: str | Path) -> PbmImage:
    """Parse a PBM (P1 ASCII or P4 binary) file, raising PbmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PbmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PbmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    data = path.read_bytes()
    header_probe = data[:16].decode("ascii", errors="replace").split()
    if not header_probe:
        raise PbmInvalidMagicError("Empty file")
    magic = header_probe[0]
    if magic not in ("P1", "P4"):
        raise PbmInvalidMagicError(f"Invalid magic: '{magic}', expected P1 or P4")

    if magic == "P4":
        return _parse_p4_binary(path, data)

    # P1 ASCII path
    raw = data.decode("ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if len(tokens) < 3:
        raise PbmInvalidHeaderError(
            f"Incomplete header: need magic, width, height; got {len(tokens)} tokens"
        )

    try:
        width = int(tokens[1])
        height = int(tokens[2])
    except ValueError as exc:
        raise PbmInvalidHeaderError(f"Invalid header values: {exc}")

    if width <= 0 or height <= 0:
        raise PbmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}"
        )

    expected_pixels = width * height
    pixel_tokens = tokens[3:]

    if len(pixel_tokens) < expected_pixels:
        raise PbmDecodeError(
            f"Not enough pixel data: expected {expected_pixels} values, got {len(pixel_tokens)}"
        )

    pixels: list[int] = []
    for i in range(expected_pixels):
        try:
            v = int(pixel_tokens[i])
        except (ValueError, IndexError) as exc:
            raise PbmDecodeError(f"Invalid pixel data at pixel {i}: {exc}")
        if v not in (0, 1):
            raise PbmDecodeError(
                f"Pixel {i} value {v} out of range — must be 0 or 1"
            )
        pixels.append(v)

    return PbmImage(
        width=width,
        height=height,
        magic=magic,
        pixels=pixels,
        path=str(path),
    )


def parse_pbm(file_path: str | Path) -> dict[str, Any]:
    """Parse a PBM file, returning a result dict (never raises)."""
    try:
        img = parse_pbm_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "magic": img.magic,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_pbm(file_path: str | Path) -> dict[str, Any]:
    """Probe a PBM file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        cleaned = _strip_comments(raw)
        tokens = cleaned.split()
        if not tokens or tokens[0] not in ("P1", "P4"):
            result["valid_header"] = False
            result["error"] = f"Invalid magic: {tokens[0] if tokens else 'empty'}"
            return result
        result["valid_header"] = True
        result["magic"] = tokens[0]
        if len(tokens) >= 3:
            result["width"] = int(tokens[1])
            result["height"] = int(tokens[2])
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# R73 Train G: image pixel statistics API
# ---------------------------------------------------------------------------

def image_pixel_stats(file_path: str | Path) -> dict[str, Any]:
    """Return pixel-level statistics for a PBM image.

    Returns a dict with:
      ok: bool
      black_count: int  — pixels with value 1 (black in PBM convention)
      white_count: int  — pixels with value 0 (white in PBM convention)
      total_pixels: int
      black_density: float  — fraction of black pixels (0.0..1.0)
      width: int, height: int, magic: str
    """
    try:
        img = parse_pbm_strict(file_path)
        black = sum(1 for p in img.pixels if p == 1)
        white = sum(1 for p in img.pixels if p == 0)
        total = len(img.pixels)
        return {
            "ok": True,
            "black_count": black,
            "white_count": white,
            "total_pixels": total,
            "black_density": round(black / total, 6) if total > 0 else 0.0,
            "width": img.width,
            "height": img.height,
            "magic": img.magic,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p1_ascii_parse",
    "p4_binary_parse",
    "bitmap_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "ppm_color",
    "pgm_grayscale",
    "pam_arbitrary_map",
    "encoding_to_pbm",
    "color_profiles",
    "metadata_extraction",
    "streaming_decode",
    "run_length_encoding",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the PBM parser (Gate 5 neutral model)."""
    return {
        "format": "pbm",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def write_pbm(
    pixels: list[int],
    width: int,
    height: int,
    file_path: str | Path,
    *,
    comment: str = "",
) -> None:
    """Write a PBM P1 (ASCII portable bitmap) file.

    Pixels must be a flat list of 0/1 integer values in row-major order.
    The list length must equal width * height. Values other than 0 or 1 are
    clamped: 0 stays 0, any non-zero becomes 1.

    This is a write-side complement to parse_pbm for roundtrip verification.
    Only P1 (ASCII) format is produced; P4 (binary) is unsupported in this track.

    Args:
        pixels: Flat row-major list of 0/1 pixel values.
        width: Image width in pixels.
        height: Image height in pixels.
        file_path: Destination file path.
        comment: Optional comment line to include in the header (no newlines).

    Raises:
        ValueError: If pixels length does not match width * height.
        PbmSizeError: If dimensions exceed MAX_DIMENSION.

    Added in R84 Train M as Netpbm write/roundtrip product advancement.
    """
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PbmSizeError(f"Dimension {width}x{height} exceeds limit {MAX_DIMENSION}")
    if len(pixels) != width * height:
        raise ValueError(
            f"pixels length {len(pixels)} does not match width*height {width * height}"
        )

    out_path = Path(file_path)
    lines = ["P1"]
    if comment:
        safe_comment = comment.replace("\n", " ").replace("\r", " ")
        lines.append(f"# {safe_comment}")
    lines.append(f"{width} {height}")
    for row_idx in range(height):
        row_start = row_idx * width
        row_pixels = pixels[row_start : row_start + width]
        row_str = " ".join("1" if p else "0" for p in row_pixels)
        lines.append(row_str)

    out_path.write_text("\n".join(lines) + "\n", encoding="ascii")
