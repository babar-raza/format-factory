"""
pbm_parser.py — PBM (Portable Bitmap) parser for format-factory-pbm.

Public API:
  parse_pbm(file_path)        — returns result dict (never raises)
  parse_pbm_strict(file_path) — raises PbmError on failure
  probe_pbm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P1 (ASCII) PBM files: magic, width, height, bitmap pixels (1=black, 0=white).
Technology: Python stdlib only (open/read/split).

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


def parse_pbm_strict(file_path: str | Path) -> PbmImage:
    """Parse a PBM file, raising PbmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PbmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PbmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    raw = path.read_text(encoding="ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if not tokens:
        raise PbmInvalidMagicError("Empty file")

    magic = tokens[0]
    if magic not in ("P1", "P4"):
        raise PbmInvalidMagicError(f"Invalid magic: '{magic}', expected P1 or P4")

    if magic == "P4":
        raise PbmDecodeError("P4 (binary) format not yet supported — P1 ASCII only")

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
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p1_ascii_parse",
    "bitmap_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p4_binary_parse",
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
