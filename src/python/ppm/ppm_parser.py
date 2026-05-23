"""
ppm_parser.py — PPM (Portable Pixmap) parser for format-factory-ppm.

Public API:
  parse_ppm(file_path)        — returns result dict (never raises)
  parse_ppm_strict(file_path) — raises PpmError on failure
  probe_ppm(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses P3 (ASCII) and P6 (binary) PPM files.
Technology: Python stdlib only (open/read/split).

R55 Train F: P6 binary decode added (TC-BINARY-PPM-001).

License: Apache-2.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 65536
MAX_MAXVAL = 65535


class PpmError(Exception):
    """Base exception for PPM parser errors."""


class PpmInvalidMagicError(PpmError):
    """Raised when file does not start with P3 or P6."""


class PpmInvalidHeaderError(PpmError):
    """Raised when header fields are invalid."""


class PpmSizeError(PpmError):
    """Raised when file or image dimensions exceed limits."""


class PpmDecodeError(PpmError):
    """Raised when pixel data is malformed."""


@dataclass
class PpmImage:
    width: int = 0
    height: int = 0
    maxval: int = 255
    magic: str = "P3"
    pixels: list[tuple[int, int, int]] = field(default_factory=list)
    path: str = ""


def _strip_comments(text: str) -> str:
    """Remove # comments from PPM text."""
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


def _parse_p6_binary(path: Path, data: bytes) -> "PpmImage":
    """Decode a P6 (binary) PPM file."""
    try:
        (width, height, maxval), data_offset = _parse_netpbm_header_bytes(data, 3)
    except (ValueError, IndexError) as exc:
        raise PpmInvalidHeaderError(f"Invalid P6 header: {exc}")

    if width <= 0 or height <= 0:
        raise PpmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PpmSizeError(f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}")
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PpmInvalidHeaderError(f"Invalid maxval: {maxval}")

    bytes_per_sample = 2 if maxval > 255 else 1
    expected_pixels = width * height
    expected_bytes = expected_pixels * 3 * bytes_per_sample
    pixel_data = data[data_offset:]

    if len(pixel_data) < expected_bytes:
        raise PpmDecodeError(
            f"Not enough binary pixel data: expected {expected_bytes} bytes, "
            f"got {len(pixel_data)}"
        )

    pixels: list[tuple[int, int, int]] = []
    if bytes_per_sample == 1:
        for i in range(expected_pixels):
            base = i * 3
            r, g, b = pixel_data[base], pixel_data[base + 1], pixel_data[base + 2]
            if r > maxval or g > maxval or b > maxval:
                raise PpmDecodeError(
                    f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
                )
            pixels.append((r, g, b))
    else:
        for i in range(expected_pixels):
            base = i * 6
            r = (pixel_data[base] << 8) | pixel_data[base + 1]
            g = (pixel_data[base + 2] << 8) | pixel_data[base + 3]
            b = (pixel_data[base + 4] << 8) | pixel_data[base + 5]
            if r > maxval or g > maxval or b > maxval:
                raise PpmDecodeError(
                    f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
                )
            pixels.append((r, g, b))

    return PpmImage(
        width=width, height=height, maxval=maxval,
        magic="P6", pixels=pixels, path=str(path),
    )


def parse_ppm_strict(file_path: str | Path) -> PpmImage:
    """Parse a PPM (P3 ASCII or P6 binary) file, raising PpmError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise PpmError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise PpmSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    data = path.read_bytes()
    header_probe = data[:16].decode("ascii", errors="replace").split()
    if not header_probe:
        raise PpmInvalidMagicError("Empty file")
    magic = header_probe[0]
    if magic not in ("P3", "P6"):
        raise PpmInvalidMagicError(f"Invalid magic: '{magic}', expected P3 or P6")

    if magic == "P6":
        return _parse_p6_binary(path, data)

    # P3 ASCII path
    raw = data.decode("ascii", errors="replace")
    cleaned = _strip_comments(raw)
    tokens = cleaned.split()

    if len(tokens) < 4:
        raise PpmInvalidHeaderError(
            f"Incomplete header: need magic, width, height, maxval; got {len(tokens)} tokens"
        )

    try:
        width = int(tokens[1])
        height = int(tokens[2])
        maxval = int(tokens[3])
    except ValueError as exc:
        raise PpmInvalidHeaderError(f"Invalid header values: {exc}")

    if width <= 0 or height <= 0:
        raise PpmInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise PpmSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}"
        )
    if maxval <= 0 or maxval > MAX_MAXVAL:
        raise PpmInvalidHeaderError(f"Invalid maxval: {maxval}")

    expected_pixels = width * height
    pixel_tokens = tokens[4:]
    expected_values = expected_pixels * 3

    if len(pixel_tokens) < expected_values:
        raise PpmDecodeError(
            f"Not enough pixel data: expected {expected_values} values, got {len(pixel_tokens)}"
        )

    pixels: list[tuple[int, int, int]] = []
    for i in range(expected_pixels):
        base = i * 3
        try:
            r = int(pixel_tokens[base])
            g = int(pixel_tokens[base + 1])
            b = int(pixel_tokens[base + 2])
        except (ValueError, IndexError) as exc:
            raise PpmDecodeError(f"Invalid pixel data at pixel {i}: {exc}")
        if r < 0 or g < 0 or b < 0 or r > maxval or g > maxval or b > maxval:
            raise PpmDecodeError(
                f"Pixel {i} value ({r},{g},{b}) out of range [0,{maxval}]"
            )
        pixels.append((r, g, b))

    return PpmImage(
        width=width,
        height=height,
        maxval=maxval,
        magic=magic,
        pixels=pixels,
        path=str(path),
    )


def parse_ppm(file_path: str | Path) -> dict[str, Any]:
    """Parse a PPM file, returning a result dict (never raises)."""
    try:
        img = parse_ppm_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "maxval": img.maxval,
            "magic": img.magic,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_ppm(file_path: str | Path) -> dict[str, Any]:
    """Probe a PPM file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        cleaned = _strip_comments(raw)
        tokens = cleaned.split()
        if not tokens or tokens[0] not in ("P3", "P6"):
            result["valid_header"] = False
            result["error"] = f"Invalid magic: {tokens[0] if tokens else 'empty'}"
            return result
        result["valid_header"] = True
        result["magic"] = tokens[0]
        if len(tokens) >= 4:
            result["width"] = int(tokens[1])
            result["height"] = int(tokens[2])
            result["maxval"] = int(tokens[3])
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "p3_ascii_parse",
    "p6_binary_parse",
    "rgb_pixel_decode",
    "comment_stripping",
    "probe",
    "dimension_extraction",
    "maxval_validation",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "pgm_grayscale",
    "pbm_bitmap",
    "pam_arbitrary_map",
    "16bit_values",
    "encoding_to_ppm",
    "color_profiles",
    "metadata_extraction",
    "streaming_decode",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the PPM parser (Gate 5 neutral model)."""
    return {
        "format": "ppm",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }
