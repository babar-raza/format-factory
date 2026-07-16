"""
xcf_parser.py — XCF (GIMP Native Image Format) parser for format-factory-xcf.

Public API:
  parse_xcf(file_path)        — returns result dict (never raises)
  parse_xcf_strict(file_path) — raises XcfError on failure
  probe_xcf(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype scope per R28 parser plan.
Parses header, property list, and layer offset table.
Does NOT decode pixel/tile data.
Technology: Python struct.unpack binary decoder (stdlib).
License: Apache-2.0
spec_concept: XCF GIMP image layer/channel/property block
"""
# ruff: noqa: F811  # analytics functions have superseding redefinitions from extraction; earlier stubs are intentionally replaced

from __future__ import annotations

import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

# XCF constants
XCF_MAGIC = b"gimp xcf "  # 9 bytes including trailing space
XCF_MAGIC_SIZE = 9
XCF_VERSION_SIZE = 4       # e.g. "v011" or "file"
XCF_HEADER_SIZE = 26       # magic(9) + version(4) + NUL(1) + width(4) + height(4) + image_type(4)
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_DIMENSION = 262144
VALID_IMAGE_TYPES = {0, 1, 2}  # 0=RGB, 1=Grayscale, 2=Indexed
IMAGE_TYPE_NAMES = {0: "RGB", 1: "Grayscale", 2: "Indexed"}

# Property constants
PROP_END = 0

class XcfError(Exception):
    """Base exception for XCF parser errors."""

class XcfInvalidMagicError(XcfError):
    """Raised when the file magic is not 'gimp xcf '."""

class XcfInvalidHeaderError(XcfError):
    """Raised when header fields are invalid."""

class XcfSizeError(XcfError):
    """Raised when file or image dimensions exceed limits."""

class XcfParseError(XcfError):
    """Raised when structural parsing fails."""


@dataclass
class XcfImage:
    # Spec authority metadata — class-level constants (no annotation = not a dataclass field)
    spec_qname: ClassVar[str] = "xcf:image"
    spec_fact_ref: ClassVar[str] = "SAL-XCF-00001"
    namespace_uri: ClassVar[str] = "https://www.gimp.org/standards/xcf"
    local_name: ClassVar[str] = "image"

    width: int = 0
    height: int = 0
    image_type: int = 0
    version: str = ""
    num_layers: int = 0
    path: str = ""
    layer_names: list = None  # type: ignore[assignment]


def _parse_header(data: bytes) -> tuple[int, int, int, str]:
    """Parse and validate XCF header.

    Returns (width, height, image_type, version).
    """
    if len(data) < XCF_HEADER_SIZE:
        raise XcfParseError(
            f"File too short: {len(data)} bytes, need at least {XCF_HEADER_SIZE}"
        )
    magic = data[:XCF_MAGIC_SIZE]
    if magic != XCF_MAGIC:
        raise XcfInvalidMagicError(
            f"Invalid magic: expected {XCF_MAGIC!r}, got {magic!r}"
        )

    # Version: 4 bytes after magic (bytes 9-12)
    version_bytes = data[XCF_MAGIC_SIZE : XCF_MAGIC_SIZE + XCF_VERSION_SIZE]
    version = version_bytes.decode("ascii", errors="replace")

    # NUL terminator at byte 13
    if data[13] != 0:
        raise XcfInvalidHeaderError(
            f"Expected NUL terminator at byte 13, got 0x{data[13]:02x}"
        )

    # Canvas properties: width, height, image_type (3x uint32 big-endian)
    width, height, image_type = struct.unpack(">III", data[14:26])

    if width == 0 or height == 0:
        raise XcfInvalidHeaderError(f"Invalid dimensions: {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise XcfSizeError(
            f"Dimensions {width}x{height} exceed limit of {MAX_DIMENSION}x{MAX_DIMENSION}"
        )
    if image_type not in VALID_IMAGE_TYPES:
        raise XcfInvalidHeaderError(
            f"Invalid image_type: {image_type}, must be one of {sorted(VALID_IMAGE_TYPES)}"
        )

    return width, height, image_type, version


def _parse_properties(data: bytes, offset: int) -> tuple[int, int]:
    """Scan the property list starting at offset.

    Returns (num_properties, offset_after_properties).
    Property format: type(uint32) + payload_length(uint32) + payload(bytes).
    Terminated by PROP_END (type=0, length=0).
    """
    pos = offset
    count = 0
    while pos + 8 <= len(data):
        prop_type, payload_len = struct.unpack(">II", data[pos : pos + 8])
        pos += 8
        if prop_type == PROP_END:
            break
        if payload_len > len(data) - pos:
            raise XcfParseError(
                f"Property payload length {payload_len} exceeds remaining data at offset {pos}"
            )
        pos += payload_len
        count += 1
    else:
        raise XcfParseError("Property list not terminated by PROP_END")
    return count, pos


def _read_xcf_string(data: bytes, offset: int) -> tuple[str, int]:
    """Read an XCF length-prefixed string. Returns (name, end_offset)."""
    if offset + 4 > len(data):
        return "", offset + 4
    (length,) = struct.unpack(">I", data[offset : offset + 4])
    end = offset + 4 + length
    s = data[offset + 4 : end - 1].decode("utf-8", errors="replace") if length > 0 else ""
    return s, end


def _parse_layer_offsets(data: bytes, offset: int) -> tuple[int, list[int], list[str]]:
    """Read the layer offset table. Returns (num_layers, offsets, names)."""
    pos = offset
    offsets: list[int] = []
    names: list[str] = []
    while pos + 4 <= len(data):
        (lo,) = struct.unpack(">I", data[pos : pos + 4])
        pos += 4
        if lo == 0:
            break
        offsets.append(lo)
        names.append(_read_xcf_string(data, lo + 12)[0])
    return len(offsets), offsets, names


def parse_xcf_strict(file_path: str | Path) -> XcfImage:
    """Parse an XCF file, raising XcfError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise XcfError(f"File not found: {path}")
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise XcfSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE}"
        )
    data = path.read_bytes()
    width, height, image_type, version = _parse_header(data)

    # Parse property list (starts at byte 26)
    _num_props, after_props = _parse_properties(data, XCF_HEADER_SIZE)

    # Parse layer offset table
    num_layers, _layer_offsets, layer_names = _parse_layer_offsets(data, after_props)

    return XcfImage(
        width=width,
        height=height,
        image_type=image_type,
        version=version,
        num_layers=num_layers,
        path=str(path),
        layer_names=layer_names,
    )


def parse_xcf(file_path: str | Path) -> dict[str, Any]:
    """Parse an XCF file, returning a result dict (never raises)."""
    try:
        img = parse_xcf_strict(file_path)
        return {
            "ok": True,
            "path": img.path,
            "width": img.width,
            "height": img.height,
            "image_type": img.image_type,
            "image_type_name": IMAGE_TYPE_NAMES.get(img.image_type, "Unknown"),
            "version": img.version,
            "num_layers": img.num_layers,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "header_parse",
    "property_list_parse",
    "layer_offset_parse",
    "probe",
    "version_detection",
    "image_type_detection",
    "dimension_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "pixel_decode",
    "tile_decode",
    "channel_data",
    "layer_compositing",
    "alpha_channel",
    "color_profiles",
    "text_layers",
    "path_data",
    "parasites",
    "compression_decode",
    "floating_selection",
    "guides_grids",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the XCF parser.

    This is the Gate 5 neutral model: an honest declaration of what the
    parser can and cannot do.  ``commercial_product_ready`` is always
    ``False`` — only a human gate review may change that.
    """
    return {
        "format": "xcf",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def probe_xcf(file_path: str | Path) -> dict[str, Any]:
    """Probe an XCF file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        data = path.read_bytes()
        if len(data) < XCF_HEADER_SIZE:
            result["valid_header"] = False
            result["error"] = f"File too short: {len(data)} bytes"
            return result
        width, height, image_type, version = _parse_header(data)
        result["valid_header"] = True
        result["width"] = width
        result["height"] = height
        result["image_type"] = image_type
        result["image_type_name"] = IMAGE_TYPE_NAMES.get(image_type, "Unknown")
        result["version"] = version
        result["file_size"] = len(data)
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result

# Analytics re-export — all xcf_* functions are in the domain module
try:
    from .xcf_image_metrics import *  # noqa: F401, F403
except ImportError:
    pass
