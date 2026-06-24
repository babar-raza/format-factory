"""
qoi_parser.py — QOI (Quite OK Image) decoder for format-factory-qoi.

Public API:
  parse_qoi(file_path)        — returns result dict (never raises)
  parse_qoi_strict(file_path) — raises QoiError on failure
  probe_qoi(file_path)        — returns header metadata without pixel decode

Implements Gate 4 prototype scope per R26 parser plan.
Full pixel decode of all 6 QOI chunk types.
Technology: Python struct.unpack binary decoder (stdlib).

License: Apache-2.0
spec_concept: QOI quite OK image header/pixel chunk
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# QOI constants
QOI_MAGIC = b"qoif"
QOI_HEADER_SIZE = 14
QOI_END_MARKER = bytes([0, 0, 0, 0, 0, 0, 0, 1])
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 16384
MAX_PIXELS = MAX_DIMENSION * MAX_DIMENSION

# Chunk tag masks
QOI_OP_INDEX = 0x00  # 0b00xxxxxx
QOI_OP_DIFF = 0x40   # 0b01xxxxxx
QOI_OP_LUMA = 0x80   # 0b10xxxxxx
QOI_OP_RUN = 0xC0    # 0b11xxxxxx
QOI_OP_RGB = 0xFE
QOI_OP_RGBA = 0xFF


UNSUPPORTED_FEATURES = frozenset({
    "animation",
    "multi_frame",
    "metadata_embedding",
    "icc_profiles",
    "exif",
    "encoding",
    "streaming_decode",
    "partial_decode",
    "thumbnail_extraction",
    "color_management",
})

SUPPORTED_FEATURES = frozenset({
    "header_parse",
    "full_pixel_decode",
    "op_rgb",
    "op_rgba",
    "op_index",
    "op_diff",
    "op_luma",
    "op_run",
    "3_channel_mode",
    "4_channel_mode",
    "srgb_colorspace",
    "linear_colorspace",
    "end_marker_validation",
    "size_guard",
    "probe_without_decode",
})


def get_capabilities() -> dict[str, Any]:
    """Return supported/unsupported feature declarations for QOI parser."""
    return {
        "format": "qoi",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
        "max_file_size": MAX_FILE_SIZE,
        "max_dimension": MAX_DIMENSION,
        "max_pixels": MAX_PIXELS,
    }


class QoiError(Exception):
    """Base exception for QOI parser errors."""


class QoiInvalidMagicError(QoiError):
    """Raised when the file magic is not 'qoif'."""


class QoiInvalidHeaderError(QoiError):
    """Raised when header fields are invalid."""


class QoiSizeError(QoiError):
    """Raised when file or image dimensions exceed limits."""


class QoiDecodeError(QoiError):
    """Raised when pixel data cannot be decoded."""


@dataclass
class QoiImage:
    spec_qname: str = "qoi:image"
    width: int = 0
    height: int = 0
    channels: int = 4
    colorspace: int = 0
    pixels: list[tuple[int, ...]] = field(default_factory=list)
    path: str = ""


def _color_hash(r: int, g: int, b: int, a: int) -> int:
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64


def _parse_header(data: bytes) -> tuple[int, int, int, int]:
    """Parse and validate QOI header. Returns (width, height, channels, colorspace)."""
    if len(data) < QOI_HEADER_SIZE:
        raise QoiDecodeError(
            f"File too short: {len(data)} bytes, need at least {QOI_HEADER_SIZE}"
        )
    magic = data[:4]
    if magic != QOI_MAGIC:
        raise QoiInvalidMagicError(
            f"Invalid magic: expected {QOI_MAGIC!r}, got {magic!r}"
        )
    width, height = struct.unpack(">II", data[4:12])
    channels = data[12]
    colorspace = data[13]

    if channels not in (3, 4):
        raise QoiInvalidHeaderError(f"Invalid channels: {channels}, must be 3 or 4")
    if colorspace not in (0, 1):
        raise QoiInvalidHeaderError(
            f"Invalid colorspace: {colorspace}, must be 0 or 1"
        )
    if width == 0 or height == 0:
        raise QoiInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise QoiSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}x{MAX_DIMENSION}"
        )
    if width * height > MAX_PIXELS:
        raise QoiSizeError(
            f"Pixel count {width * height} exceeds limit of {MAX_PIXELS}"
        )
    return width, height, channels, colorspace


def _decode_pixels(
    data: bytes, width: int, height: int, channels: int
) -> list[tuple[int, ...]]:
    """Decode QOI pixel data from all 6 chunk types."""
    pixel_count = width * height
    pixels: list[tuple[int, ...]] = []

    # Running color hash array
    index = [(0, 0, 0, 0)] * 64
    r, g, b, a = 0, 0, 0, 255  # Previous pixel

    pos = QOI_HEADER_SIZE
    end = len(data) - 8  # Exclude end marker

    while len(pixels) < pixel_count and pos < end:
        byte = data[pos]

        if byte == QOI_OP_RGB:
            if pos + 3 >= end:
                raise QoiDecodeError("Truncated QOI_OP_RGB chunk")
            r = data[pos + 1]
            g = data[pos + 2]
            b = data[pos + 3]
            pos += 4
        elif byte == QOI_OP_RGBA:
            if pos + 4 >= end:
                raise QoiDecodeError("Truncated QOI_OP_RGBA chunk")
            r = data[pos + 1]
            g = data[pos + 2]
            b = data[pos + 3]
            a = data[pos + 4]
            pos += 5
        elif (byte & 0xC0) == QOI_OP_INDEX:
            idx = byte & 0x3F
            r, g, b, a = index[idx]
            pos += 1
        elif (byte & 0xC0) == QOI_OP_DIFF:
            dr = ((byte >> 4) & 0x03) - 2
            dg = ((byte >> 2) & 0x03) - 2
            db = (byte & 0x03) - 2
            r = (r + dr) & 0xFF
            g = (g + dg) & 0xFF
            b = (b + db) & 0xFF
            pos += 1
        elif (byte & 0xC0) == QOI_OP_LUMA:
            if pos + 1 >= end:
                raise QoiDecodeError("Truncated QOI_OP_LUMA chunk")
            byte2 = data[pos + 1]
            dg = (byte & 0x3F) - 32
            dr_dg = ((byte2 >> 4) & 0x0F) - 8
            db_dg = (byte2 & 0x0F) - 8
            r = (r + dg + dr_dg) & 0xFF
            g = (g + dg) & 0xFF
            b = (b + dg + db_dg) & 0xFF
            pos += 2
        elif (byte & 0xC0) == QOI_OP_RUN:
            run_length = (byte & 0x3F) + 1
            for _ in range(min(run_length, pixel_count - len(pixels))):
                if channels == 3:
                    pixels.append((r, g, b))
                else:
                    pixels.append((r, g, b, a))
            idx_hash = _color_hash(r, g, b, a)
            index[idx_hash] = (r, g, b, a)
            pos += 1
            continue  # Skip the append below — already added
        else:
            pos += 1
            continue

        idx_hash = _color_hash(r, g, b, a)
        index[idx_hash] = (r, g, b, a)
        if channels == 3:
            pixels.append((r, g, b))
        else:
            pixels.append((r, g, b, a))

    if len(pixels) < pixel_count:
        raise QoiDecodeError(
            f"Decoded {len(pixels)} pixels, expected {pixel_count}"
        )

    # Verify end marker
    marker = data[end : end + 8]
    if marker != QOI_END_MARKER:
        raise QoiDecodeError(
            f"Invalid end marker: expected {QOI_END_MARKER.hex()}, got {marker.hex()}"
        )

    return pixels


def parse_qoi_strict(file_path: str | Path) -> QoiImage:
    """Parse a QOI file, raising QoiError on any problem."""
    path = Path(file_path)
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise QoiSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE}"
        )
    data = path.read_bytes()
    width, height, channels, colorspace = _parse_header(data)
    pixels = _decode_pixels(data, width, height, channels)
    return QoiImage(
        width=width,
        height=height,
        channels=channels,
        colorspace=colorspace,
        pixels=pixels,
        path=str(path),
    )


def parse_qoi(file_path: str | Path) -> dict[str, Any]:
    """Parse a QOI file, returning a result dict (never raises)."""
    try:
        img = parse_qoi_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "channels": img.channels,
            "colorspace": img.colorspace,
            "pixel_count": len(img.pixels),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_qoi(file_path: str | Path) -> dict[str, Any]:
    """Probe a QOI file for header metadata without decoding pixels."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        data = path.read_bytes()
        if len(data) < QOI_HEADER_SIZE:
            result["valid_header"] = False
            result["error"] = f"File too short: {len(data)} bytes"
            return result
        width, height, channels, colorspace = _parse_header(data)
        result["valid_header"] = True
        result["width"] = width
        result["height"] = height
        result["channels"] = channels
        result["colorspace"] = colorspace
        result["file_size"] = len(data)
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result



# ---------------------------------------------------------------------------
# Analytics functions moved to qoi_analytics.py (TC-HEAL-FORMATS-BATCH2)
# ---------------------------------------------------------------------------
try:
    from .image_document import *  # noqa: F401, F403
except ImportError:
    pass
